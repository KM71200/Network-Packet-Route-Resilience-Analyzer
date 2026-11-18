# Network Packet Route Resilience Analyzer

A Python-based network routing and resilience analysis tool developed as part of the **Design and Analysis of Algorithms (DAA)** project.

## Overview

The Network Packet Route Resilience Analyzer finds the minimum-cost route between a source and destination while respecting a maximum edge constraint.

The project uses **Dynamic Programming** as its primary optimization technique. It also simulates communication link failures, recalculates alternative routes, and evaluates network resilience.

## Key Features

- Minimum-cost route calculation using Dynamic Programming.
- Maximum number of edges (K) constraint.
- Route reconstruction using parent pointers.
- Link failure simulation.
- Alternative route calculation after failures.
- Critical link analysis.
- Network Resilience Score calculation.
- Comparison with Greedy and Brute Force approaches.
- Interactive visualization using Streamlit.

## Algorithms

- Dynamic Programming — Primary optimization algorithm.
- Greedy Algorithm — Comparison approach.
- Brute Force — Baseline for validating optimal results.

## Technology Stack

- Python
- Streamlit
- NetworkX
- Matplotlib

## Academic Project

**Course:** Design and Analysis of Algorithms (DAA)  
**Project:** Network Packet Route Resilience Analyzer
