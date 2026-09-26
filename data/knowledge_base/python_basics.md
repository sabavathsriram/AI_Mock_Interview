# Python Programming Basics

## Introduction to Python

Python is a high-level, interpreted programming language known for its simplicity and readability. It was created by Guido van Rossum and first released in 1991.

## Key Features

- **Easy to Learn**: Python has a simple syntax that resembles natural English
- **Interpreted**: Python code is executed line by line
- **Dynamically Typed**: Variables don't need type declarations
- **Object-Oriented**: Python supports OOP concepts
- **Extensive Libraries**: Python has a rich standard library

## Python Data Types

### Primitives
- int: Integer numbers
- float: Decimal numbers
- str: Text strings
- bool: True or False

### Collections
- list: Ordered, mutable collection
- tuple: Ordered, immutable collection
- dict: Key-value pairs
- set: Unique, unordered elements

## Control Structures

### Conditional Statements
```
if condition:
    # code
elif another_condition:
    # code
else:
    # code
```

### Loops
- for loop: Iterate over sequences
- while loop: Repeat while condition is true

## Functions

Functions are reusable blocks of code that perform specific tasks.

```python
def function_name(parameters):
    """Docstring"""
    # code
    return value
```

## Exception Handling

Python uses try-except blocks for error handling:

```python
try:
    # code that might raise exception
except ExceptionType:
    # handle exception
finally:
    # cleanup code
```

## Object-Oriented Programming

Python supports OOP with classes and objects:

```python
class MyClass:
    def __init__(self, value):
        self.value = value
    
    def method(self):
        return self.value
```

## Common Interview Questions

1. What is the difference between a list and a tuple?
2. What is list comprehension and how is it used?
3. Explain decorators in Python
4. What is the GIL (Global Interpreter Lock)?
5. How does Python manage memory?

## Best Practices

- Follow PEP 8 style guidelines
- Use meaningful variable names
- Write docstrings for functions
- Use virtual environments for projects
- Write unit tests
- Handle exceptions appropriately
