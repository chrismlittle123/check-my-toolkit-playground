# Python file with intentional lint issues for testing

import os  # F401: unused import
import sys  # used below

def greet(name):
    x = 1  # F841: local variable assigned but never used
    print(f"Hello, {name}!")
    return sys.version

def add(a, b):
    return a + b

# Long line that exceeds 88 characters limit - this is intentionally very long to test the line-length configuration setting
