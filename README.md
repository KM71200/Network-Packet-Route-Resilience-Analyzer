# Network Packet Route Resilience Analyzer Using Dynamic Programming

## Project Overview

The Network Packet Route Resilience Analyzer is a Design and Analysis of Algorithms (DAA) project that analyzes routing in a weighted directed network.

The system finds the minimum-cost route between a source and destination while considering a maximum number of permitted links (K). It also simulates network link failures, calculates alternative routes, identifies vulnerable network links, evaluates network resilience, and compares different routing algorithms.

Dynamic Programming is the primary algorithm used in the project.

---

## Objectives

The main objectives of the project are:

- Find the minimum-cost route between a source and destination.
- Enforce a maximum K-link constraint.
- Simulate individual network link failures.
- Find alternative routes when the original route is affected.
- Identify critical and high-impact network links.
- Calculate a Network Resilience Score.
- Compare Dynamic Programming with Greedy and Brute Force approaches.
- Visualize the network, routes, and failed links using an interactive interface.

---

## Technology Stack

- Python
- Streamlit
- NetworkX
- Matplotlib
- JSON

---

## Project Structure

```text
Network-Packet-Route-Resilience/
│
├── app.py
├── requirements.txt
├── README.md
│
├── algorithms/
│   ├── dynamic_programming.py
│   └── algorithm_comparison.py
│
├── network/
│   ├── network_graph.py
│   └── failure_simulation.py
│
├── analysis/
│   └── resilience_analysis.py
│
├── visualization/
│   └── network_visualization.py
│
├── tests/
│   └── test_cases.py
│
└── data/
    └── sample_network.json
```

---

## Sample Network

The sample network contains the following weighted directed connections:

| Edge | Cost |
|---|---:|
| A → B | 2 |
| A → C | 4 |
| B → C | 1 |
| B → D | 7 |
| C → D | 2 |
| C → E | 5 |
| D → E | 1 |

Default input:

```text
Source = A
Destination = E
K = 3
```

The minimum-cost route is:

```text
A → C → D → E
```

Total cost:

```text
7
```

Number of links:

```text
3
```

---

## Dynamic Programming Approach

Dynamic Programming is the core algorithm of the project.

The DP state is:

```text
DP[k][v] = Minimum cost to reach vertex v
           from the source using at most k edges.
```

Initialization:

```text
DP[0][source] = 0
DP[0][v] = infinity for all other vertices
```

For each value of k, the algorithm considers whether the previous best route should be retained or whether reaching a node through one of its incoming edges produces a lower cost.

Predecessor information is maintained so that the selected minimum-cost route can be reconstructed.

The K constraint ensures that the selected route contains at most the maximum permitted number of links.

---

## Link Failure Simulation

The application allows the user to select an individual network link and simulate its failure.

If the failed link does not affect the original optimal route, the original route is retained.

If the failed link belongs to the original route, the edge is removed from a copy of the network and the Dynamic Programming algorithm is executed again to find an alternative route.

If no feasible alternative route exists within the K-link constraint, the application reports that the destination is unreachable.

### Example

For:

```text
Source = A
Destination = E
K = 3
```

the original route is:

```text
A → C → D → E
Cost = 7
```

If:

```text
C → D
```

fails, the alternative minimum-cost route calculated by the implemented system is:

```text
A → B → C → E
Cost = 8
```

Therefore:

```text
Cost Increase = 8 - 7 = 1
```

---

## Network Resilience Analysis

The system automatically tests individual network-edge failures.

Each directed edge is temporarily failed independently, and the routing algorithm checks whether a feasible route between the same source and destination is still available within the same K constraint.

The Network Resilience Score is calculated as:

```text
Resilience Score =
(Recoverable Single-Edge Failures / Total Tested Single-Edge Failures) × 100
```

For the default sample network with:

```text
Source = A
Destination = E
K = 3
```

the current implementation produces:

```text
Total Tested Failures = 7
Recoverable Failures = 7
Unrecoverable Failures = 0
Network Resilience Score = 100%
```

This score represents resilience only under the simulated single-edge failure scenarios. It should not be interpreted as real-world network reliability.

---

## Critical Link Analysis

Each tested edge failure is analyzed according to its effect on routing.

The analysis uses the following categories:

- **Critical** — No feasible alternative route exists.
- **High-Impact** — An alternative route exists, but the route cost increases significantly.
- **Low-Impact** — The failure causes little or no increase in the minimum route cost.

The current analysis uses a defined percentage cost-increase threshold to distinguish between high-impact and low-impact failures.

The application displays the failed link, classification, alternative route, alternative cost, and cost increase.

---

## Algorithm Comparison

The project compares three routing approaches.

### Dynamic Programming

Dynamic Programming is the primary algorithm.

It finds the minimum-cost route while respecting the maximum K-link constraint.

### Greedy Algorithm

The Greedy baseline selects the locally cheapest available outgoing edge at every step while avoiding previously visited nodes.

It does not guarantee a globally optimal route and may fail even when another feasible route exists.

### Brute Force

Brute Force enumerates feasible simple routes for small graphs and selects the minimum-cost route.

It is used as a validation baseline for the Dynamic Programming result on small test cases.

### Default Sample Comparison

For:

```text
Source = A
Destination = E
K = 3
```

the current application produces:

| Algorithm | Route | Cost | Links Used |
|---|---|---:|---:|
| Dynamic Programming | A → C → D → E | 7 | 3 |
| Greedy | No Route | N/A | 0 |
| Brute Force | A → C → D → E | 7 | 3 |

The Brute Force result matches the Dynamic Programming result for the sample network, validating the optimal route.

The Greedy approach fails because its locally cheapest choices do not necessarily lead to the destination within the K-link constraint.

---

## Network Visualization

NetworkX and Matplotlib are used to visualize the network and routing behaviour.

The visualization uses:

- **Gray** — Normal network links
- **Blue** — Original optimal route
- **Green** — Alternative route
- **Red dashed** — Failed link

Edge weights are displayed directly on the graph.

---

## Installation

### 1. Requirements

Python 3 is required.

### 2. Install Dependencies

Open a terminal inside the project directory and run:

```bash
python3 -m pip install -r requirements.txt
```

The required Python packages are:

```text
streamlit
networkx
matplotlib
```

---

## Running the Application

From the project directory, run:

```bash
python3 -m streamlit run app.py
```

Streamlit will start the application and provide a local browser address.

Open the provided address to use the interactive prototype.

---

## Using the Application

### Minimum-Cost Routing

1. Select the network.
2. Select a source node.
3. Select a destination node.
4. Enter the maximum number of links K.
5. Click **Find Optimal Route**.
6. View the route, total cost, number of links, and network visualization.

### Link Failure Simulation

1. Select a network link.
2. Click **Simulate Failure**.
3. The system checks whether the original route is affected.
4. If necessary, an alternative route is calculated.
5. The original route, failed link, and alternative route are visualized.

### Resilience Analysis

Click **Run Resilience Analysis** to test individual edge failures and display:

- Network Resilience Score
- Recoverable failures
- Unrecoverable failures
- Critical-link analysis
- Alternative routes
- Cost increases

### Algorithm Comparison

Click **Compare Algorithms** to compare:

- Dynamic Programming
- Greedy
- Brute Force

---

## Tested Cases

The integrated prototype has been tested for:

- Normal minimum-cost route calculation.
- Different values of K.
- Route changes caused by the K constraint.
- No feasible route within the selected K constraint.
- Same source and destination validation.
- Failure of a link belonging to the optimal route.
- Alternative route calculation after failure.
- Failure of a link not belonging to the optimal route.
- Retaining the original route when the failed link does not affect it.
- Automatic individual edge-failure analysis.
- Network Resilience Score calculation.
- Critical-link classification.
- Dynamic Programming, Greedy, and Brute Force comparison.
- Brute Force validation of the Dynamic Programming result.

### Example K-Constraint Test

For:

```text
Source = A
Destination = E
K = 2
```

the optimal route becomes:

```text
A → C → E
Cost = 9
Links = 2
```

For:

```text
Source = A
Destination = E
K = 1
```

no feasible route exists because there is no direct edge from A to E.

---

## Limitations and Risks

- The project uses simulated network topologies rather than real routers.
- Network edge weights are synthetic and fixed.
- Only individual link failures are currently analyzed.
- Simultaneous multiple-link failures are outside the current scope.
- Real-time network congestion is not modeled.
- Packet loss and changing bandwidth are not directly considered.
- Actual packet transmission and live network rerouting are outside the scope of the prototype.
- Brute Force is suitable only for small networks because its computational cost increases rapidly as the network grows.
- The Greedy algorithm is only a simple comparison baseline and is not guaranteed to find an optimal route.
- The Network Resilience Score represents only the tested single-edge failure scenarios and is not a measure of real-world network reliability.

---

## Team Contributions

### Karmanya Maletha

Implemented the core Dynamic Programming algorithm, including DP initialization and recurrence, the K-link constraint, predecessor tracking, route reconstruction, and unreachable-destination handling.

### Chirag Mayor

Developed the weighted directed network representation, JSON dataset handling, graph generation, input validation, and sample network dataset.

### Aayushi Iyer

Implemented individual link-failure simulation, route-impact detection, adaptive rerouting, and automatic single-edge failure testing.

### Divyanshu Singh

Implemented the Greedy and Brute Force comparison algorithms, critical-link analysis, and Network Resilience Score functionality.

### Yashvi Manojkumar Patel

Developed the Streamlit frontend and network visualization, integrated the project modules into the final interactive application, resolved integration issues, and tested the complete prototype.

---

## Conclusion

The Network Packet Route Resilience Analyzer demonstrates how Dynamic Programming can be applied to a constrained network-routing problem.

The project extends minimum-cost routing by incorporating a maximum-link constraint, link-failure simulation, adaptive rerouting, proactive resilience analysis, critical-link identification, algorithm comparison, and interactive network visualization.

The final prototype provides a reproducible way to study how routing decisions and individual link failures affect a simulated network.