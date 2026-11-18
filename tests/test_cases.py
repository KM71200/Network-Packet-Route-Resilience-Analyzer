import math
import networkx as nx
import pytest

from algorithms.algorithm_comparison import greedy_route, brute_force_route
from analysis.resilience_analysis import (
    calculate_resilience_score,
    identify_critical_links,
)


def create_common_graph():
    graph = nx.DiGraph()
    edges = [
        ("A", "B", 2),
        ("A", "C", 4),
        ("B", "C", 1),
        ("B", "D", 7),
        ("C", "D", 2),
        ("C", "E", 5),
        ("D", "E", 1),
    ]
    for u, v, cost in edges:
        graph.add_edge(u, v, weight=cost)
    return graph


def test_brute_force_common_network():
    result = brute_force_route(create_common_graph(), "A", "E", 3)
    assert result["path"] == ["A", "C", "D", "E"]
    assert result["cost"] == 7
    assert result["links"] == 3


def test_greedy_respects_k_and_can_fail():
    result = greedy_route(create_common_graph(), "A", "E", 3)
    # The locally cheapest choices lead toward B -> C -> D, which would
    # require a fourth edge to reach E. Greedy does not backtrack.
    assert result["path"] == []
    assert math.isinf(result["cost"])


def test_brute_force_route_with_k_two():
    # A -> C -> E is feasible in two links and costs 9.
    result = brute_force_route(create_common_graph(), "A", "E", 2)
    assert result["path"] == ["A", "C", "E"]
    assert result["cost"] == 9
    assert result["links"] == 2


def test_brute_force_after_failed_edge():
    graph = create_common_graph()
    graph.remove_edge("C", "D")
    result = brute_force_route(graph, "A", "E", 3)
    # The actual cheapest alternative is A -> B -> C -> E (cost 8).
    # A -> B -> D -> E costs 10, but is not optimal in the supplied graph.
    assert result["path"] == ["A", "B", "C", "E"]
    assert result["cost"] == 8
    assert result["links"] == 3


def test_resilience_score():
    failures = [
        {"failed_edge": ("A", "B"), "alternative": {"path": ["A", "C", "D", "E"], "cost": 7}},
        {"failed_edge": ("C", "D"), "alternative": {"path": ["A", "B", "D", "E"], "cost": 10}},
        {"failed_edge": ("D", "E"), "alternative": {"path": [], "cost": math.inf}},
        {"failed_edge": ("A", "C"), "alternative": {"path": ["A", "B", "D", "E"], "cost": 10}},
    ]
    result = calculate_resilience_score(failures)
    assert result == {
        "score": 75.0,
        "recoverable_failures": 3,
        "unrecoverable_failures": 1,
        "total_tested_failures": 4,
    }


def test_critical_link_classification():
    failures = [
        {"failed_edge": ("D", "E"), "alternative": {"path": [], "cost": math.inf}},
        {"failed_edge": ("C", "D"), "alternative": {"path": ["A", "B", "D", "E"], "cost": 10}},
        {"failed_edge": ("A", "B"), "alternative": {"path": ["A", "C", "D", "E"], "cost": 7}},
    ]
    ranked = identify_critical_links(failures, original_cost=7, high_impact_percent=20)
    assert ranked[0]["edge"] == ("D", "E")
    assert ranked[0]["category"] == "Critical"
    assert ranked[1]["edge"] == ("C", "D")
    assert ranked[1]["category"] == "High-Impact"
    assert ranked[2]["category"] == "Low-Impact"


def test_dp_matches_brute_force_when_dp_module_is_available():
    try:
        from algorithms.dynamic_programming import find_optimal_route
    except ImportError:
        pytest.skip("Karmanya's dynamic_programming.py is not integrated yet.")

    graph = create_common_graph()
    dp = find_optimal_route(graph, "A", "E", 3)
    brute = brute_force_route(graph, "A", "E", 3)
    assert dp["cost"] == brute["cost"] == 7
    assert dp["links"] == brute["links"] == 3
