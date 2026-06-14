from typing import Any

def is_valid(value: Any):
    return type(value) is str and value != ""