from pathlib import Path
from math import inf

import streamlit as st

# Project modules
from network.network_graph import load_network_config, validate_inputs
from algorithms.dynamic_programming import find_shortest_path
from network.failure_simulation import (
    simulate_edge_failure,
    test_all_single_edge_failures,
)
from algorithms.algorithm_comparison import compare_algorithms
from analysis.resilience_analysis import analyze_resilience
from visualization.network_visualization import draw_network


# -------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------

st.set_page_config(
    page_title="Network Packet Route Resilience Analyzer",
    page_icon="🌐",
    layout="wide",
)

st.title("🌐 Network Packet Route Resilience Analyzer")

st.write(
    "Find minimum-cost network routes using Dynamic Programming, "
    "simulate link failures, and evaluate network resilience."
)

st.divider()


# -------------------------------------------------
# LOAD NETWORK DATA
# -------------------------------------------------

DATA_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "sample_network.json"
)

try:
    graph, default_source, default_destination, default_k = (
        load_network_config(str(DATA_FILE))
    )

except Exception as error:
    st.error(f"Unable to load network: {error}")
    st.stop()

nodes = list(graph.nodes())


# -------------------------------------------------
# ROUTE CONFIGURATION
# -------------------------------------------------

st.header("Route Configuration")

st.selectbox(
    "Select Network",
    ["Sample Network"],
)

col1, col2, col3 = st.columns(3)

with col1:
    source = st.selectbox(
        "Source Node",
        nodes,
        index=nodes.index(default_source),
    )

with col2:
    destination = st.selectbox(
        "Destination Node",
        nodes,
        index=nodes.index(default_destination),
    )

with col3:
    k = st.number_input(
        "Maximum Number of Links (K)",
        min_value=1,
        max_value=max(1, len(nodes)),
        value=default_k,
        step=1,
    )


# -------------------------------------------------
# OPTIMAL ROUTE
# -------------------------------------------------

if st.button(
    "Find Optimal Route",
    type="primary",
):
    if source == destination:
        st.error(
            "Please select different source and destination nodes."
        )

    else:
        try:
            validate_inputs(
                graph,
                source,
                destination,
                int(k),
            )

            result = find_shortest_path(
                graph,
                source,
                destination,
                int(k),
            )

            if result["reachable"]:
                route = result["path"]
                cost = result["cost"]
                links = result["edges_used"]

                st.success(
                    "Optimal route found successfully."
                )

                metric1, metric2, metric3 = st.columns(3)

                with metric1:
                    st.metric(
                        "Optimal Route",
                        " → ".join(map(str, route)),
                    )

                with metric2:
                    st.metric(
                        "Total Cost",
                        cost,
                    )

                with metric3:
                    st.metric(
                        "Links Used",
                        links,
                    )

                st.subheader(
                    "Optimal Route Visualization"
                )

                route_figure = draw_network(
                    graph,
                    original_route=route,
                )

                st.pyplot(route_figure)

            else:
                st.error(
                    "No feasible route exists within "
                    "the selected K-link constraint."
                )

        except Exception as error:
            st.error(
                f"Routing error: {error}"
            )


# -------------------------------------------------
# NETWORK VISUALIZATION
# -------------------------------------------------

st.divider()

st.header("Network Visualization")

st.write(
    "The graph below represents the weighted directed network."
)

network_figure = draw_network(graph)

st.pyplot(network_figure)


# -------------------------------------------------
# LINK FAILURE SIMULATION
# -------------------------------------------------

st.divider()

st.header("Link Failure Simulation")

st.write(
    "Select a network link to simulate its failure "
    "and observe the routing behaviour."
)

edge_options = list(graph.edges())

failed_edge = st.selectbox(
    "Select Failed Link",
    edge_options,
    format_func=lambda edge: f"{edge[0]} → {edge[1]}",
)

if st.button("Simulate Failure"):
    if source == destination:
        st.error(
            "Please select different source and destination nodes."
        )

    else:
        try:
            failure_result = simulate_edge_failure(
                graph,
                source,
                destination,
                int(k),
                failed_edge,
                find_shortest_path,
            )

            original_route = failure_result[
                "original_route"
            ]

            original_cost = failure_result[
                "original_cost"
            ]

            st.write(
                f"**Failed Link:** "
                f"{failed_edge[0]} → {failed_edge[1]}"
            )

            if failure_result["status"] == "unaffected":
                st.info(
                    "The failed link does not affect "
                    "the original optimal route."
                )

                retained_route = failure_result[
                    "alternative_route"
                ]

                st.write(
                    "**Original Route Retained:** "
                    + " → ".join(
                        map(str, retained_route)
                    )
                )

                st.write(
                    f"**Route Cost:** "
                    f"{failure_result['alternative_cost']}"
                )

                failure_figure = draw_network(
                    graph,
                    original_route=original_route,
                    failed_edge=failed_edge,
                )

                st.pyplot(failure_figure)

            elif failure_result["status"] == "rerouted":
                alternative_route = failure_result[
                    "alternative_route"
                ]

                alternative_cost = failure_result[
                    "alternative_cost"
                ]

                cost_increase = failure_result[
                    "cost_increase"
                ]

                st.success(
                    "The original route was affected. "
                    "An alternative route was found."
                )

                metric1, metric2, metric3 = st.columns(3)

                with metric1:
                    st.metric(
                        "Alternative Route",
                        " → ".join(
                            map(str, alternative_route)
                        ),
                    )

                with metric2:
                    st.metric(
                        "Alternative Cost",
                        alternative_cost,
                        delta=cost_increase,
                    )

                with metric3:
                    st.metric(
                        "Links Used",
                        len(alternative_route) - 1,
                    )

                st.write(
                    f"Original Route Cost: **{original_cost}**"
                )

                st.subheader(
                    "Rerouting Visualization"
                )

                failure_figure = draw_network(
                    graph,
                    original_route=original_route,
                    failed_edge=failed_edge,
                    alternative_route=alternative_route,
                )

                st.pyplot(failure_figure)

            else:
                st.error(
                    "The original route was affected and "
                    "no feasible alternative route exists "
                    "within the K-link constraint."
                )

                failure_figure = draw_network(
                    graph,
                    original_route=original_route,
                    failed_edge=failed_edge,
                )

                st.pyplot(failure_figure)

        except Exception as error:
            st.error(
                f"Failure simulation error: {error}"
            )


# -------------------------------------------------
# NETWORK RESILIENCE ANALYSIS
# -------------------------------------------------

st.divider()

st.header("Network Resilience Analysis")

st.write(
    "Test individual link failures to identify vulnerable "
    "connections and evaluate network resilience."
)

if st.button("Run Resilience Analysis"):
    if source == destination:
        st.error(
            "Please select different source and destination nodes."
        )

    else:
        try:
            all_failures = test_all_single_edge_failures(
                graph,
                source,
                destination,
                int(k),
                find_shortest_path,
            )

            original_cost = all_failures[
                "original_cost"
            ]

            failure_results = all_failures[
                "results"
            ]

            resilience_input = []

            for item in failure_results:
                alternative_route = item[
                    "alternative_route"
                ]

                resilience_input.append(
                    {
                        "failed_edge": item[
                            "failed_edge"
                        ],
                        "alternative_path":
                            alternative_route or [],
                        "alternative_cost": item[
                            "alternative_cost"
                        ],
                        "alternative_links": (
                            len(alternative_route) - 1
                            if alternative_route
                            else 0
                        ),
                    }
                )

            resilience_result = analyze_resilience(
                resilience_input,
                original_cost,
            )

            resilience_data = resilience_result[
                "resilience"
            ]

            critical_links = resilience_result[
                "critical_links"
            ]

            st.subheader("Resilience Summary")

            metric1, metric2, metric3 = st.columns(3)

            with metric1:
                st.metric(
                    "Network Resilience Score",
                    f"{resilience_data['score']}%",
                )

            with metric2:
                st.metric(
                    "Recoverable Failures",
                    resilience_data[
                        "recoverable_failures"
                    ],
                )

            with metric3:
                st.metric(
                    "Unrecoverable Failures",
                    resilience_data[
                        "unrecoverable_failures"
                    ],
                )

            st.subheader("Critical Link Analysis")

            critical_link_table = []

            for item in critical_links:
                edge = item["edge"]
                cost_increase = item[
                    "cost_increase"
                ]

                if item["alternative_path"]:
                    route_text = " → ".join(
                        map(
                            str,
                            item["alternative_path"],
                        )
                    )
                else:
                    route_text = "No Route"

                critical_link_table.append(
                    {
                        "Link":
                            f"{edge[0]} → {edge[1]}",
                        "Category":
                            item["category"],
                        "Alternative Route":
                            route_text,
                        "Alternative Cost": (
                            item["alternative_cost"]
                            if item["reachable"]
                            else "N/A"
                        ),
                        "Cost Increase": (
                            cost_increase
                            if cost_increase is not None
                            else "N/A"
                        ),
                    }
                )

            st.dataframe(
                critical_link_table,
                use_container_width=True,
            )

        except Exception as error:
            st.error(
                f"Resilience analysis error: {error}"
            )


# -------------------------------------------------
# ALGORITHM COMPARISON
# -------------------------------------------------

st.divider()

st.header("Algorithm Comparison")

st.write(
    "Compare Dynamic Programming with Greedy "
    "and Brute Force routing approaches."
)

if st.button("Compare Algorithms"):
    if source == destination:
        st.error(
            "Please select different source and destination nodes."
        )

    else:
        try:
            comparison = compare_algorithms(
                graph,
                source,
                destination,
                int(k),
                find_shortest_path,
            )

            comparison_table = []

            for algorithm, result in comparison.items():
                path = result.get(
                    "path",
                    [],
                )

                cost = result.get(
                    "cost",
                    inf,
                )

                links = result.get(
                    "links",
                    result.get(
                        "edges_used",
                        0,
                    ),
                )

                comparison_table.append(
                    {
                        "Algorithm": algorithm,
                        "Route": (
                            " → ".join(map(str, path))
                            if path
                            else "No Route"
                        ),
                        "Cost": (
                            cost
                            if cost != inf
                            else None
                        ),
                        "Links Used": links,
                    }
                )

            st.dataframe(
                comparison_table,
                use_container_width=True,
            )

        except Exception as error:
            st.error(
                f"Algorithm comparison error: {error}"
            )


# -------------------------------------------------
# FOOTER
# -------------------------------------------------

st.divider()

st.caption(
    "Design and Analysis of Algorithms PBL — "
    "Network Packet Route Resilience Analyzer"
)