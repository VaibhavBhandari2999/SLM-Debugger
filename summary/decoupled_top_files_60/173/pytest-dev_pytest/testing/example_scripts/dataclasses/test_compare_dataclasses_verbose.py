from dataclasses import dataclass
from dataclasses import field


def test_dataclasses_verbose():
    """
    Generate a Python docstring for the provided function.
    
    This function demonstrates the usage of the `dataclass` decorator from the `dataclasses` module to create a simple data class. The `SimpleDataObject` class has two fields, `field_a` and `field_b`, both of which are integers. The `field` function is used to initialize these fields.
    
    Parameters:
    None
    
    Returns:
    None
    
    Example:
    >>> left = SimpleDataObject(1, "b")
    """

    @dataclass
    class SimpleDataObject:
        field_a: int = field()
        field_b: int = field()

    left = SimpleDataObject(1, "b")
    right = SimpleDataObject(1, "c")

    assert left == right
