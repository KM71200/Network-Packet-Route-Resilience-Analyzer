from copy import deepcopy
from math import inf
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

DPResult = Dict[str, Any]
DPSolver = Callable[[Any, Any, Any, int], DPResult]


def _normalise_dp_result(result: Any) -> DPResult:
    """Accept the documented dictionary result or a (path, cost) tuple."""
    if isinstance(result, dict):
        path = result.get("path")
        cost = result.get("cost", inf)
    elif isinstance(result, tuple) and len(result) == 2:
        path, cost = result
    else:
        raise TypeError(
            "dp_solver must return {'path': ..., 'cost': ...} or (path, cost)"
        )

    if path is None:
        return {"path": None, "cost": inf}
    path = list(path)
    if not path:
        return {"path": None, "cost": inf}
    return {"path": path, "cost": cost}


def _route_uses_edge(path: Optional[List[Any]], edge: Tuple[Any, Any]) -> bool:
    if not path or len(path) < 2:
        return False
    return any((path[i], path[i + 1]) == edge for i in range(len(path) - 1))


def _edge_cost(graph: Any, path: Optional[List[Any]]) -> float:
    """Calculate a route's cost using the graph's 'weight' edge attribute."""
    if not path or len(path) < 2:
        return 0 if path else inf
    total = 0
    for u, v in zip(path, path[1:]):
        if not graph.has_edge(u, v):
            return inf
        total += graph[u][v].get("weight", 1)
    return total


def simulate_edge_failure(
    graph: Any,
    source: Any,
    destination: Any,
    max_edges: int,
    failed_edge: Tuple[Any, Any],
    dp_solver: DPSolver,
) -> DPResult:
    """
    Simulate one selected edge failure and reroute if required.

    The input graph is never modified. The returned dictionary contains:
    failed_edge, original_route, original_cost, affected, status,
    alternative_route, alternative_cost, and cost_increase.
    """
    if max_edges < 0:
        raise ValueError("max_edges must be zero or greater")
    if not hasattr(graph, "is_directed") or not graph.is_directed():
        raise TypeError("graph must be a directed NetworkX graph")
    if not graph.has_edge(*failed_edge):
        raise ValueError(f"Edge {failed_edge!r} does not exist in the graph")

    original = _normalise_dp_result(
        dp_solver(graph, source, destination, max_edges)
    )
    original_path = original["path"]
    original_cost = original["cost"]
    affected = _route_uses_edge(original_path, failed_edge)

    result = {
        "failed_edge": failed_edge,
        "original_route": original_path,
        "original_cost": original_cost,
        "affected": affected,
        "status": "",
        "alternative_route": None,
        "alternative_cost": inf,
        "cost_increase": None,
    }

    if not affected:
        result.update({
            "status": "unaffected",
            "alternative_route": original_path,
            "alternative_cost": original_cost,
            "cost_increase": 0,
        })
        return result

    # Work on a copy: the original network remains unchanged for future tests.
    failed_graph = deepcopy(graph)
    failed_graph.remove_edge(*failed_edge)

    alternative = _normalise_dp_result(
        dp_solver(failed_graph, source, destination, max_edges)
    )
    if alternative["path"] is None:
        result["status"] = "unreachable"
        return result

    result.update({
        "status": "rerouted",
        "alternative_route": alternative["path"],
        "alternative_cost": alternative["cost"],
        "cost_increase": alternative["cost"] - original_cost,
    })
    return result


def test_all_single_edge_failures(
    graph: Any,
    source: Any,
    destination: Any,
    max_edges: int,
    dp_solver: DPSolver,
) -> Dict[str, Any]:
    """
    Test every directed edge independently (one failure per test).

    Returns the baseline route, one result per edge, critical/high/low-impact
    classifications, and a scenario-based resilience score.
    """
    baseline = _normalise_dp_result(
        dp_solver(graph, source, destination, max_edges)
    )
    if baseline["path"] is None:
        raise ValueError(
            "The original graph has no feasible route; failure impact "
            "and resilience score cannot be evaluated."
        )

    edge_results = []
    for u, v in list(graph.edges()):
        edge_results.append(
            simulate_edge_failure(
                graph, source, destination, max_edges, (u, v), dp_solver
            )
        )

    total = len(edge_results)
    feasible = sum(r["status"] != "unreachable" for r in edge_results)
    score = (feasible / total * 100) if total else 100.0

    # Impact classification is intentionally transparent:
    # critical = no route; high = cost rises; low = route cost unchanged
    # or the failed edge did not affect the selected original route.
    for item in edge_results:
        if item["status"] == "unreachable":
            item["impact"] = "Critical Link"
        elif item["cost_increase"] > 0:
            item["impact"] = "High-Impact Link"
        else:
            item["impact"] = "Low-Impact Link"

    # Critical first, then descending cost increase, then low-impact.
    edge_results.sort(
        key=lambda r: (
            0 if r["impact"] == "Critical Link" else
            1 if r["impact"] == "High-Impact Link" else 2,
            -(r["cost_increase"] or 0),
        )
    )

    return {
        "original_route": baseline["path"],
        "original_cost": baseline["cost"],
        "max_edges": max_edges,
        "tested_edges": total,
        "successful_alternative_count": feasible,
        "resilience_score": score,
        "results": edge_results,
    }


def format_failure_report(result: DPResult) -> str:
    """Create a readable console report for one manual failure."""
    u, v = result["failed_edge"]
    lines = [
        f"Failed link: {u} -> {v}",
        f"Original route: {' -> '.join(map(str, result['original_route']))}",
        f"Original cost: {result['original_cost']}",
    ]
    if result["status"] == "unaffected":
        lines += [
            "Result: Original route is unaffected.",
            f"Route retained: {' -> '.join(map(str, result['alternative_route']))}",
        ]
    elif result["status"] == "rerouted":
        lines += [
            "Result: Original route was affected; DP rerouting completed.",
            f"Alternative route: {' -> '.join(map(str, result['alternative_route']))}",
            f"Alternative cost: {result['alternative_cost']}",
            f"Cost increase: {result['cost_increase']}",
        ]
    else:
        lines += [
            "Result: Original route was affected.",
            "Alternative route: No feasible route exists within the K-edge limit.",
        ]
    return "\n".join(lines)
