# Python Programming Interview Guide

## Python Fundamentals

### Data Types
- **Immutable**: int, float, str, tuple, frozenset, bool
- **Mutable**: list, dict, set, bytearray

### Variables and Scope
- Python is dynamically typed
- LEGB Rule: Local, Enclosing, Global, Built-in
- Global variables accessible but modifiable with 'global' keyword
- Nonlocal for nested functions

## Collections

### Lists
- Ordered, mutable collection
- List comprehension: [x*2 for x in range(10)]
- Common methods: append(), extend(), insert(), remove(), pop(), sort()

### Tuples
- Ordered, immutable collection
- Used as dictionary keys
- Unpacking: a, b = (1, 2)

### Dictionaries
- Key-value pairs, mutable
- Keys must be hashable (immutable)
- Iteration: for key, value in dict.items()
- Default value: dict.get(key, default)

### Sets
- Unordered, unique elements
- Set operations: union (|), intersection (&), difference (-)
- Common methods: add(), remove(), discard(), clear()

## Functions

### Function Definition
- def keyword
- Arguments: positional, default, *args, **kwargs
- Return statement optional (returns None)
- Docstrings for documentation

### Lambda Functions
- Anonymous functions: lambda x: x * 2
- Used with map(), filter(), sorted()

### Decorators
- Functions that modify other functions
- @decorator syntax
- Common: @staticmethod, @classmethod, @property

## Object-Oriented Programming

### Classes
- Define with 'class' keyword
- __init__ for constructor
- self reference to instance
- Attributes and methods

### Inheritance
- class Child(Parent): 
- super() to call parent methods
- Method resolution order (MRO)

### Special Methods
- __str__: String representation
- __repr__: Unambiguous representation
- __eq__: Equality comparison
- __hash__: Hash value for sets/dicts
- __len__: Length

### Properties
- @property decorator for getters
- @setter for custom setters
- Provides encapsulation without explicit getters/setters

## Exception Handling

### Try-Except-Finally
```python
try:
    # code that may raise exception
except SpecificException:
    # handle specific exception
except Exception:
    # handle general exceptions
finally:
    # cleanup code
```

### Common Exceptions
- ValueError: Invalid argument value
- TypeError: Wrong data type
- KeyError: Dictionary key not found
- IndexError: List index out of range
- AttributeError: Attribute doesn't exist
- ZeroDivisionError: Division by zero

## File Handling

### Reading Files
- open(filename, 'r')
- read(), readline(), readlines()
- with statement for automatic closing

### Writing Files
- open(filename, 'w') - overwrite
- open(filename, 'a') - append
- write(), writelines()

## Python Performance Tips

### Time Complexity
- List access: O(1), search: O(n)
- Dict/Set access: O(1) average
- List insert/delete: O(n)

### Optimization Strategies
- Use list comprehension over loops
- Use generators for memory efficiency
- Use built-in functions (they're C-optimized)
- Use appropriate data structure
- Avoid unnecessary conversions

### List Comprehension vs Generator
- List: [x*2 for x in range(1000)] - creates full list
- Generator: (x*2 for x in range(1000)) - lazy evaluation
- Generator more memory efficient for large datasets

## Important Modules

### Collections
- defaultdict: Dict with default values
- Counter: Count elements frequency
- namedtuple: Lightweight class

### Itertools
- chain(): Combine iterables
- combinations(): All combinations
- permutations(): All permutations
- groupby(): Group consecutive elements

### Functools
- reduce(): Apply function cumulatively
- lru_cache: Memoization decorator
- partial: Fix arguments

## Python 3 Features

### Type Hints
```python
def add(a: int, b: int) -> int:
    return a + b
```

### F-Strings
```python
name = "Alice"
print(f"Hello {name}")
print(f"Value: {value:.2f}")
```

### Context Managers
- with statement
- __enter__ and __exit__ methods
- Resource management

## Common Interview Questions

### String Manipulation
- Reverse string: s[::-1]
- Check palindrome: s == s[::-1]
- Split and join: separator.join(list)

### List Operations
- Sort: sorted(list) returns new, list.sort() in-place
- Reverse: reversed(list) returns iterator
- Flatten: [item for sublist in list for item in sublist]

### Dictionary Operations
- Merge: {**dict1, **dict2} (Python 3.5+)
- Keys/values: dict.keys(), dict.values()
- Pop with default: dict.pop(key, default)
