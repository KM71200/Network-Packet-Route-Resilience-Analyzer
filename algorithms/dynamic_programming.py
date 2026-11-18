import networkx as nx
import math


def find_shortest_path(graph, source, destination, K):

    # 1. Validate inputs
    if not isinstance(K, int) or isinstance(K, bool) or K < 0:
        raise ValueError("K must be a non-negative integer.")

    if source not in graph:
        raise ValueError("Source node does not exist in the graph.")

    if destination not in graph:
        raise ValueError("Destination node does not exist in the graph.")

    if not graph.is_directed():
        raise ValueError("The graph must be directed.")

    # 2. Validate edge weights
    for u, v, data in graph.edges(data=True):
        weight = data.get("weight")

        if (
            not isinstance(weight, (int, float))
            or isinstance(weight, bool)
            or not math.isfinite(weight)
            or weight < 0
        ):
            raise ValueError("All edge weights must be finite and non-negative.")

    nodes = list(graph.nodes())

    # 3. Initialize DP table
    # dp[k][v] = minimum cost to reach v using at most k edges

    dp = [
        {node: float("inf") for node in nodes}
        for _ in range(K + 1)
    ]

    # Parent table stores the previous DP state
    parent = [
        {node: None for node in nodes}
        for _ in range(K + 1)
    ]

    dp[0][source] = 0

    # 4. Fill the DP table
    for k in range(1, K + 1):

        # Option 1: Carry forward the previous best cost
        for node in nodes:
            dp[k][node] = dp[k - 1][node]
            parent[k][node] = (k - 1, node)

        # Option 2: Reach a node through an incoming edge
        for u, v, data in graph.edges(data=True):

            weight = data["weight"]

            if dp[k - 1][u] == float("inf"):
                continue

            new_cost = dp[k - 1][u] + weight

            if new_cost < dp[k][v]:
                dp[k][v] = new_cost
                parent[k][v] = (k - 1, u)

    # 5. Check whether destination is reachable
    if dp[K][destination] == float("inf"):
        return {
            "path": [],
            "cost": float("inf"),
            "edges_used": 0,
            "reachable": False
        }

    # 6. Reconstruct the actual route
    path = [destination]

    k = K
    current = destination

    while not (k == 0 and current == source):

        previous = parent[k][current]

        if previous is None:
            raise RuntimeError("Route reconstruction failed.")

        previous_k, previous_node = previous

        # Add a node only when an actual edge was used
        if previous_node != current:
            path.append(previous_node)

        k = previous_k
        current = previous_node

    path.reverse()

    # 7. Return results
    return {
        "path": path,
        "cost": dp[K][destination],
        "edges_used": len(path) - 1,
        "reachable": True
    }
