from math import inf
from typing import Any, Dict, List

Result = Dict[str, Any]


def _make_result(path: List[Any], cost: float) -> Result:
    """Create the common result format used by routing algorithms."""

    if not path:
        return {
            "path": [],
            "cost": inf,
            "links": 0
        }

    return {
        "path": path,
        "cost": cost,
        "links": len(path) - 1
    }


# -------------------------------------------------
# GREEDY ALGORITHM
# -------------------------------------------------

def greedy_route(
    graph,
    source,
    destination,
    k,
    weight="weight"
) -> Result:
    """
    Basic greedy routing.

    At each node, choose the cheapest outgoing edge
    that does not revisit a node and does not exceed K links.

    This is a simple baseline and does not guarantee
    the globally optimal route.
    """

    if k < 0 or source not in graph or destination not in graph:
        return _make_result([], inf)

    if source == destination:
        return _make_result([source], 0)

    path = [source]
    visited = {source}
    total_cost = 0
    current = source

    for _ in range(k):

        if current == destination:
            return _make_result(path, total_cost)

        candidates = []

        for neighbor in graph.successors(current):

            if neighbor in visited:
                continue

            edge_data = graph.get_edge_data(
                current,
                neighbor
            )

            edge_cost = edge_data.get(weight, 1)

            if edge_cost < 0:
                raise ValueError(
                    "Greedy routing requires "
                    "non-negative edge weights."
                )

            candidates.append(
                (
                    edge_cost,
                    str(neighbor),
                    neighbor
                )
            )

        if not candidates:
            break

        # Select locally cheapest available edge
        edge_cost, _, next_node = min(candidates)

        path.append(next_node)
        visited.add(next_node)

        total_cost += edge_cost
        current = next_node

    if current == destination:
        return _make_result(
            path,
            total_cost
        )

    return _make_result([], inf)


# -------------------------------------------------
# BRUTE FORCE ALGORITHM
# -------------------------------------------------

def brute_force_route(
    graph,
    source,
    destination,
    k,
    weight="weight"
) -> Result:
    """
    Enumerate all simple source-to-destination paths
    containing at most K edges.

    Intended only for small graphs and validation.
    """

    if k < 0 or source not in graph or destination not in graph:
        return _make_result([], inf)

    if source == destination:
        return _make_result(
            [source],
            0
        )

    best_path = []
    best_cost = inf

    def dfs(
        current,
        path,
        visited,
        cost
    ):
        nonlocal best_path, best_cost

        # Destination reached
        if current == destination:

            if cost < best_cost:
                best_cost = cost
                best_path = path.copy()

            return

        # Maximum number of links reached
        if len(path) - 1 == k:
            return

        for neighbor in graph.successors(current):

            if neighbor in visited:
                continue

            edge_cost = graph[current][neighbor].get(
                weight,
                1
            )

            if edge_cost < 0:
                raise ValueError(
                    "Brute force routing requires "
                    "non-negative edge weights."
                )

            # Since weights are non-negative,
            # stop exploring if already more expensive
            # than the best known route.
            if cost + edge_cost >= best_cost:
                continue

            visited.add(neighbor)
            path.append(neighbor)

            dfs(
                neighbor,
                path,
                visited,
                cost + edge_cost
            )

            path.pop()
            visited.remove(neighbor)

    dfs(
        source,
        [source],
        {source},
        0
    )

    return _make_result(
        best_path,
        best_cost
    )


# -------------------------------------------------
# ALGORITHM COMPARISON
# -------------------------------------------------

def compare_algorithms(
    graph,
    source,
    destination,
    k,
    dp_function=None
) -> Dict[str, Result]:
    """
    Run Dynamic Programming, Greedy and Brute Force
    on the same network.

    Karmanya's DP implementation is used by default:

    algorithms.dynamic_programming.find_shortest_path
    """

    # Import DP only when another function
    # has not explicitly been supplied.
    if dp_function is None:

        try:
            from algorithms.dynamic_programming import (
                find_shortest_path
            )

        except ImportError as exc:
            raise ImportError(
                "DP module not found. "
                "Add algorithms/dynamic_programming.py "
                "with find_shortest_path("
                "graph, source, destination, k)."
            ) from exc

        dp_function = find_shortest_path

    # Run Dynamic Programming
    dp_result = dp_function(
        graph,
        source,
        destination,
        k
    )

    # Karmanya's DP uses 'edges_used'.
    # Convert it to the common 'links' field
    # used by this comparison module.
    if "edges_used" in dp_result:
        dp_result["links"] = dp_result["edges_used"]

    # Run baseline algorithms
    greedy_result = greedy_route(
        graph,
        source,
        destination,
        k
    )

    brute_result = brute_force_route(
        graph,
        source,
        destination,
        k
    )

    return {
        "DP": dp_result,
        "Greedy": greedy_result,
        "Brute Force": brute_result
    }