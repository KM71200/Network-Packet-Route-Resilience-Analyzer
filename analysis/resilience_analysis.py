from math import inf
from typing import Any, Dict, Iterable, List


# -------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------

def _edge_from_result(result):
    """
    Extract the failed edge from a failure simulation result.
    Supports both 'failed_edge' and 'edge' keys.
    """

    edge = result.get(
        "failed_edge",
        result.get("edge")
    )

    if edge is None:
        raise ValueError(
            "Each failure result must contain "
            "'failed_edge' or 'edge'."
        )

    return tuple(edge)


def _alternative_from_result(result):
    """
    Extract alternative route information.

    Supports both nested and flattened result formats
    so that the module can integrate with the failure
    simulation implementation.
    """

    alternative = result.get("alternative")

    # Nested result format
    if isinstance(alternative, dict):

        path = alternative.get("path", [])
        cost = alternative.get("cost", inf)

        links = alternative.get(
            "links",
            alternative.get(
                "edges_used",
                max(0, len(path) - 1)
            )
        )

        return {
            "path": path or [],
            "cost": cost,
            "links": links
        }

    # Flattened result format
    path = result.get(
        "alternative_path",
        result.get("path", [])
    )

    cost = result.get(
        "alternative_cost",
        result.get("cost", inf)
    )

    links = result.get(
        "alternative_links",
        result.get(
            "links",
            result.get(
                "edges_used",
                max(0, len(path) - 1)
            )
        )
    )

    return {
        "path": path or [],
        "cost": cost,
        "links": links
    }


# -------------------------------------------------
# CRITICAL LINK IDENTIFICATION
# -------------------------------------------------

def identify_critical_links(
    failure_results: Iterable[Dict[str, Any]],
    original_cost: float,
    high_impact_percent: float = 20.0,
) -> List[Dict[str, Any]]:
    """
    Rank individual failed edges according to impact.

    Classification:

    Critical:
        No feasible alternative route exists.

    High-Impact:
        Alternative exists, but route cost increases
        by at least the configured threshold.

    Low-Impact:
        Failure causes little or no increase in cost.
    """

    if high_impact_percent < 0:
        raise ValueError(
            "high_impact_percent cannot be negative."
        )

    ranked = []

    for item in failure_results:

        edge = _edge_from_result(item)

        alternative = _alternative_from_result(item)

        path = alternative.get("path") or []

        cost = alternative.get(
            "cost",
            inf
        )

        reachable = (
            bool(path)
            and cost != inf
        )

        # No alternative route
        if not reachable:

            category = "Critical"

            delta = None
            increase_percent = None

        else:

            # Change in route cost
            delta = cost - original_cost

            if original_cost > 0:

                increase_percent = (
                    delta / original_cost
                ) * 100

            else:

                increase_percent = (
                    0.0
                    if delta <= 0
                    else inf
                )

            # Classify impact
            if (
                increase_percent >= high_impact_percent
                and delta > 0
            ):
                category = "High-Impact"

            else:
                category = "Low-Impact"

        ranked.append({
            "edge": edge,
            "category": category,
            "reachable": reachable,
            "alternative_path": path,
            "alternative_cost": (
                cost if reachable else None
            ),
            "cost_increase": delta,
            "increase_percent": increase_percent,
        })

    # Ranking priority
    priority = {
        "Critical": 0,
        "High-Impact": 1,
        "Low-Impact": 2
    }

    ranked.sort(
        key=lambda row: (
            priority[row["category"]],
            -(
                row["increase_percent"]
                if row["increase_percent"] is not None
                else 0
            ),
            str(row["edge"]),
        )
    )

    return ranked


# -------------------------------------------------
# NETWORK RESILIENCE SCORE
# -------------------------------------------------

def calculate_resilience_score(
    failure_results: Iterable[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate the Network Resilience Score.

    Resilience Score =
    Recoverable single-edge failures
    -------------------------------- × 100
    Total tested single-edge failures
    """

    results = list(failure_results)

    total = len(results)

    recoverable = 0

    for item in results:

        alternative = _alternative_from_result(
            item
        )

        if (
            alternative.get("path")
            and alternative.get("cost", inf) != inf
        ):
            recoverable += 1

    unrecoverable = (
        total - recoverable
    )

    score = (
        recoverable / total * 100
        if total
        else 0.0
    )

    return {
        "score": round(score, 2),
        "recoverable_failures": recoverable,
        "unrecoverable_failures": unrecoverable,
        "total_tested_failures": total,
    }


# -------------------------------------------------
# COMPLETE RESILIENCE ANALYSIS
# -------------------------------------------------

def analyze_resilience(
    failure_results: Iterable[Dict[str, Any]],
    original_cost: float,
    high_impact_percent: float = 20.0,
) -> Dict[str, Any]:
    """
    Return both:
    1. Network Resilience Score
    2. Ranked critical-link analysis
    """

    results = list(
        failure_results
    )

    resilience = calculate_resilience_score(
        results
    )

    critical_links = identify_critical_links(
        results,
        original_cost,
        high_impact_percent
    )

    return {
        "resilience": resilience,
        "critical_links": critical_links,
        "high_impact_threshold_percent":
            high_impact_percent,
    }