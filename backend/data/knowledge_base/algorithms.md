# Algorithms Interview Guide

## Sorting Algorithms

### Bubble Sort
- Repeatedly swaps adjacent elements if they are in wrong order
- Time: O(n²), Space: O(1)
- Stable: Yes
- When to use: Educational purposes only

### Selection Sort
- Finds minimum element and places at beginning
- Time: O(n²), Space: O(1)
- Stable: No
- When to use: When memory is limited

### Insertion Sort
- Builds sorted array by inserting elements one by one
- Time: O(n²), Space: O(1)
- Stable: Yes
- When to use: Small arrays, nearly sorted data

### Merge Sort
- Divide and conquer approach
- Time: O(n log n), Space: O(n)
- Stable: Yes
- When to use: Large arrays, external sorting

### Quick Sort
- Partition array around pivot
- Average: O(n log n), Worst: O(n²), Space: O(log n)
- Stable: No (standard implementation)
- When to use: General-purpose sorting, in-place preferred

### Heap Sort
- Uses heap data structure
- Time: O(n log n), Space: O(1)
- Stable: No
- When to use: When worst-case guarantee needed

## Searching Algorithms

### Linear Search
- Check each element sequentially
- Time: O(n)
- When to use: Unsorted small arrays

### Binary Search
- Divide search space in half each iteration
- Time: O(log n)
- Requires: Sorted array
- When to use: Large sorted arrays

## Dynamic Programming

Dynamic programming solves problems by breaking them into overlapping subproblems and storing results.

### Key Concepts
1. **Optimal Substructure**: Optimal solution contains optimal solutions to subproblems
2. **Overlapping Subproblems**: Same subproblems appear multiple times

### Approaches
- **Top-Down (Memoization)**: Recursion with caching
- **Bottom-Up (Tabulation)**: Iterative solution building from base cases

### Common Problems
- Fibonacci sequence
- Longest Common Subsequence (LCS)
- Knapsack problem
- Coin change problem
- Matrix chain multiplication
- Edit distance (Levenshtein)
- Longest increasing subsequence

## Graph Algorithms

### Traversal

**Breadth-First Search (BFS)**
- Explores graph level by level
- Time: O(V + E)
- Space: O(V)
- Uses: Level-order traversal, shortest path in unweighted graphs

**Depth-First Search (DFS)**
- Explores graph depth-wise
- Time: O(V + E)
- Space: O(V)
- Uses: Topological sorting, cycle detection

### Shortest Path

**Dijkstra's Algorithm**
- Finds shortest path from source to all vertices
- Time: O(V² + E) or O((V + E) log V) with heap
- Requirement: Non-negative weights
- Greedy approach

**Bellman-Ford Algorithm**
- Finds shortest paths allowing negative weights
- Time: O(V·E)
- Can detect negative cycles
- Dynamic programming approach

**Floyd-Warshall Algorithm**
- Finds shortest paths between all pairs
- Time: O(V³)
- Space: O(V²)
- Allows negative weights

### Minimum Spanning Tree

**Kruskal's Algorithm**
- Sorts edges, adds edges not creating cycle
- Time: O(E log E)
- Uses Union-Find

**Prim's Algorithm**
- Grows tree from arbitrary vertex
- Time: O(V² + E) or O((V + E) log V)
- Uses priority queue

### Topological Sort
- Linear ordering of vertices in directed acyclic graph
- Time: O(V + E)
- Uses: Dependency resolution, task scheduling

## Backtracking

Systematically tries all possible solutions by exploring paths and backtracking when no solution found.

### Common Problems
- N-Queens problem
- Sudoku solver
- Maze solving
- Permutations and combinations
- Word search in 2D matrix

## Greedy Algorithms

Makes locally optimal choice at each step, hoping to find global optimum.

### Common Applications
- Activity selection problem
- Huffman coding
- Dijkstra's algorithm
- Kruskal's/Prim's algorithm
- Job sequencing with deadlines

### Note: Greedy doesn't always produce optimal solution
