# Python file with type errors for testing

def greet(name: str) -> str:
    return f"Hello, {name}!"

def add(a: int, b: int) -> int:
    return a + b

# Type error - string returned but int expected
def get_number() -> int:
    return "not a number"

# Type error - wrong argument type
result = add("1", "2")
