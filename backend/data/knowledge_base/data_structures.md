# Data Structures Interview Guide

## Arrays and Lists

An array is a contiguous memory allocation for storing elements of the same type. Arrays provide O(1) random access but have fixed size in most languages.

### Time Complexity
- Access: O(1)
- Search: O(n)
- Insertion: O(n)
- Deletion: O(n)

## Linked Lists

A linked list is a linear data structure where elements are stored in nodes. Each node contains data and a reference to the next node.

### Types of Linked Lists
1. **Singly Linked List**: Each node points to the next node only
2. **Doubly Linked List**: Each node has pointers to both next and previous nodes
3. **Circular Linked List**: Last node points back to the first node

### Time Complexity
- Access: O(n)
- Search: O(n)
- Insertion: O(1) at beginning, O(n) in general
- Deletion: O(1) at beginning, O(n) in general

## Stacks

A stack is a Last-In-First-Out (LIFO) data structure. Elements are added and removed from the same end (top).

### Operations
- **Push**: Add element to top - O(1)
- **Pop**: Remove element from top - O(1)
- **Peek**: View top element - O(1)

### Common Uses
- Expression evaluation (infix to postfix conversion)
- Backtracking (undo/redo operations)
- Function call stack
- Browser back button

## Queues

A queue is a First-In-First-Out (FIFO) data structure. Elements are added at rear and removed from front.

### Types
- **Simple Queue**: Basic FIFO structure
- **Circular Queue**: Front and rear wrap around
- **Priority Queue**: Elements served based on priority
- **Deque**: Double-ended queue allowing insertion/deletion at both ends

### Operations
- **Enqueue**: Add to rear - O(1)
- **Dequeue**: Remove from front - O(1)
- **Front**: View front element - O(1)

## Hash Tables

A hash table stores key-value pairs using a hash function to compute an index.

### Collision Resolution
1. **Chaining**: Store multiple values in linked list at same hash index
2. **Open Addressing**: Find another empty slot
   - Linear probing: Check next slot
   - Quadratic probing: Check slot at quadratic distance
   - Double hashing: Use another hash function

### Time Complexity (Average)
- Search: O(1)
- Insert: O(1)
- Delete: O(1)

### Time Complexity (Worst Case)
- All operations: O(n) when hash function creates poor distribution

## Trees

A tree is a hierarchical data structure with nodes connected by edges.

### Binary Trees
- Each node has at most 2 children (left and right)
- Height: Maximum distance from root to leaf
- Balanced tree: Height is O(log n)

### Binary Search Trees (BST)
- Left subtree values < node value < right subtree values
- Enables efficient searching
- Average: O(log n), Worst: O(n)

### AVL Trees
- Self-balancing BST
- Maintains height difference ≤ 1 between subtrees
- Rotations rebalance the tree
- Time: O(log n) for all operations

### Red-Black Trees
- Self-balancing BST with color property
- Ensures rough balance
- Time: O(log n) guaranteed

### Complete Binary Trees
- All levels filled except possibly last
- Last level filled left to right
- Used in heap implementations

## Heaps

A heap is a complete binary tree satisfying heap property.

### Min Heap
- Parent value ≤ child values
- Root is minimum element

### Max Heap
- Parent value ≥ child values
- Root is maximum element

### Operations
- Insert: O(log n)
- Delete min/max: O(log n)
- Get min/max: O(1)

### Uses
- Priority queues
- Heap sort algorithm
- Finding k-th largest element
