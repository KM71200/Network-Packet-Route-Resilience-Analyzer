import json
import random
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import networkx as nx


def create_graph() -> nx.DiGraph:
    """Return an empty weighted directed graph."""
    return nx.DiGraph()


def add_connection(graph: nx.DiGraph, source: str, destination: str, weight: float) -> None:
    """Add one directed connection after validating its endpoints and weight."""
    if not isinstance(graph, nx.DiGraph):
        raise TypeError("graph must be a networkx.DiGraph.")
    if not isinstance(source, str) or not source.strip():
        raise ValueError("Source node must be a non-empty string.")
    if not isinstance(destination, str) or not destination.strip():
        raise ValueError("Destination node must be a non-empty string.")
    if source == destination:
        raise ValueError("Self-loop connections are not allowed in this prototype.")
    if isinstance(weight, bool) or not isinstance(weight, (int, float)):
        raise ValueError("Edge weight must be a number.")
    if weight < 0:
        raise ValueError("Edge weight must be non-negative.")
    graph.add_edge(source.strip(), destination.strip(), weight=weight)


def validate_graph(graph: nx.DiGraph) -> bool:
    """Validate the graph format required by the DP and comparison modules."""
    if not isinstance(graph, nx.DiGraph):
        raise TypeError("Graph must be a networkx.DiGraph (weighted directed graph).")
    if graph.number_of_nodes() == 0:
        raise ValueError("Graph must contain at least one node.")

    for source, destination, data in graph.edges(data=True):
        if "weight" not in data:
            raise ValueError(f"Edge {source} -> {destination} is missing a weight.")
        weight = data["weight"]
        if isinstance(weight, bool) or not isinstance(weight, (int, float)):
            raise ValueError(f"Weight for edge {source} -> {destination} must be numeric.")
        if weight < 0:
            raise ValueError(f"Weight for edge {source} -> {destination} cannot be negative.")
    return True


def validate_inputs(graph: nx.DiGraph, source: str, destination: str, k: int) -> bool:
    """Validate source, destination and maximum-link constraint K."""
    validate_graph(graph)

    if source not in graph:
        raise ValueError(f"Invalid source node '{source}'. Available nodes: {list(graph.nodes)}")
    if destination not in graph:
        raise ValueError(
            f"Invalid destination node '{destination}'. Available nodes: {list(graph.nodes)}"
        )
    if source == destination:
        raise ValueError("Source and destination must be different nodes.")
    if isinstance(k, bool) or not isinstance(k, int):
        raise ValueError("K must be an integer.")
    if k <= 0:
        raise ValueError("K must be greater than 0.")
    return True


def _validate_dataset(data: Dict[str, Any]) -> None:
    """Validate JSON structure before converting it into a graph."""
    if not isinstance(data, dict):
        raise ValueError("Dataset root must be a JSON object.")
    if "nodes" not in data or "edges" not in data:
        raise ValueError("Dataset must contain 'nodes' and 'edges'.")
    if not isinstance(data["nodes"], list) or not data["nodes"]:
        raise ValueError("'nodes' must be a non-empty list.")
    if len(data["nodes"]) != len(set(data["nodes"])):
        raise ValueError("Node names must be unique.")
    if any(not isinstance(node, str) or not node.strip() for node in data["nodes"]):
        raise ValueError("Every node name must be a non-empty string.")
    if not isinstance(data["edges"], list):
        raise ValueError("'edges' must be a list.")

    node_set = set(data["nodes"])
    seen_edges = set()
    for index, edge in enumerate(data["edges"], start=1):
        if not isinstance(edge, dict):
            raise ValueError(f"Edge #{index} must be a JSON object.")
        if not {"source", "destination", "weight"}.issubset(edge):
            raise ValueError(f"Edge #{index} must contain source, destination and weight.")
        u, v, w = edge["source"], edge["destination"], edge["weight"]
        if u not in node_set or v not in node_set:
            raise ValueError(f"Edge #{index} refers to an undefined node: {u} -> {v}.")
        if u == v:
            raise ValueError(f"Self-loop is not allowed: {u} -> {v}.")
        if (u, v) in seen_edges:
            raise ValueError(f"Duplicate directed edge found: {u} -> {v}.")
        seen_edges.add((u, v))
        if isinstance(w, bool) or not isinstance(w, (int, float)) or w < 0:
            raise ValueError(f"Edge {u} -> {v} must have a non-negative numeric weight.")


def graph_from_data(data: Dict[str, Any]) -> nx.DiGraph:
    """Convert a validated dataset dictionary into a ``networkx.DiGraph``."""
    _validate_dataset(data)
    graph = create_graph()
    graph.add_nodes_from(data["nodes"])
    for edge in data["edges"]:
        add_connection(graph, edge["source"], edge["destination"], edge["weight"])
    validate_graph(graph)
    return graph


def load_graph_from_json(file_path: str) -> nx.DiGraph:
    """Load a weighted directed graph from the project's JSON dataset format."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Network dataset not found: {file_path}")
    if path.suffix.lower() != ".json":
        raise ValueError("Network dataset must be a .json file.")

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in network dataset: {exc}") from exc

    return graph_from_data(data)


def load_network_config(file_path: str) -> Tuple[nx.DiGraph, str, str, int]:
    """Load graph plus default source, destination and K from a JSON file.

    Returns:
        (graph, source, destination, k)
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Network dataset not found: {file_path}")

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in network dataset: {exc}") from exc

    graph = graph_from_data(data)
    defaults = data.get("defaults")
    if not isinstance(defaults, dict):
        raise ValueError("Dataset must contain a 'defaults' object for source, destination and k.")

    try:
        source = defaults["source"]
        destination = defaults["destination"]
        k = defaults["k"]
    except KeyError as exc:
        raise ValueError("'defaults' must contain source, destination and k.") from exc

    validate_inputs(graph, source, destination, k)
    return graph, source, destination, k


def generate_sample_graph() -> nx.DiGraph:
    """Create the common five-node test network used by all team members."""
    data = {
        "nodes": ["A", "B", "C", "D", "E"],
        "edges": [
            {"source": "A", "destination": "B", "weight": 2},
            {"source": "A", "destination": "C", "weight": 4},
            {"source": "B", "destination": "C", "weight": 1},
            {"source": "B", "destination": "D", "weight": 7},
            {"source": "C", "destination": "D", "weight": 2},
            {"source": "C", "destination": "E", "weight": 5},
            {"source": "D", "destination": "E", "weight": 1},
        ],
    }
    return graph_from_data(data)


def generate_random_graph(
    num_nodes: int = 6,
    edge_probability: float = 0.35,
    min_weight: int = 1,
    max_weight: int = 10,
    seed: Optional[int] = None,
) -> nx.DiGraph:
    """Generate a reproducible random weighted directed graph for extra testing."""
    if isinstance(num_nodes, bool) or not isinstance(num_nodes, int) or num_nodes < 2:
        raise ValueError("num_nodes must be an integer of at least 2.")
    if not isinstance(edge_probability, (int, float)) or not 0 <= edge_probability <= 1:
        raise ValueError("edge_probability must be between 0 and 1.")
    if not isinstance(min_weight, int) or not isinstance(max_weight, int):
        raise ValueError("Weight limits must be integers.")
    if min_weight < 0 or max_weight < min_weight:
        raise ValueError("Use non-negative weights with max_weight >= min_weight.")

    rng = random.Random(seed)
    labels = [chr(ord("A") + i) if i < 26 else f"N{i + 1}" for i in range(num_nodes)]
    graph = create_graph()
    graph.add_nodes_from(labels)

    # Add a simple forward chain first so the generated graph is not empty and
    # has at least one route from the first node to the last node.
    for i in range(num_nodes - 1):
        add_connection(graph, labels[i], labels[i + 1], rng.randint(min_weight, max_weight))

    for source in labels:
        for destination in labels:
            if source != destination and not graph.has_edge(source, destination):
                if rng.random() < edge_probability:
                    add_connection(graph, source, destination, rng.randint(min_weight, max_weight))

    validate_graph(graph)
    return graph


def graph_summary(graph: nx.DiGraph) -> Dict[str, Any]:
    """Return a simple serializable summary useful for debugging/integration."""
    validate_graph(graph)
    return {
        "nodes": list(graph.nodes),
        "edges": [
            {"source": u, "destination": v, "weight": data["weight"]}
            for u, v, data in graph.edges(data=True)
        ],
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
    }


if __name__ == "__main__":
    sample_path = Path(__file__).resolve().parent.parent / "data" / "sample_network.json"
    graph, source, destination, k = load_network_config(str(sample_path))
    print("Network loaded successfully.")
    print("Nodes:", list(graph.nodes))
    print("Edges:")
    for u, v, data in graph.edges(data=True):
        print(f"  {u} -> {v}, weight = {data['weight']}")
    print(f"Default input: source={source}, destination={destination}, K={k}")
    print("Graph is valid and ready for the DP algorithm.")
