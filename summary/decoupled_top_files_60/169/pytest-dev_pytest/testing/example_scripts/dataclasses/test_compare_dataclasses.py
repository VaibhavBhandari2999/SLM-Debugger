from dataclasses import dataclass
from dataclasses import field


def test_dataclasses():
    """
    This function demonstrates the usage of the `dataclasses` module in Python to create a simple data class. The `SimpleDataObject` class is defined with two fields: `field_a` and `field_b`. Both fields are initialized with default values. The function creates two instances of `SimpleDataObject` and checks for equality.
    
    Key Parameters:
    - None
    
    Keywords:
    - dataclasses: A Python module used to create simple data classes.
    
    Input:
    - None
    
    Output:
    - The function does
    """

    @dataclass
    class SimpleDataObject(object):
        field_a: int = field()
        field_b: int = field()

    left = SimpleDataObject(1, "b")
    right = SimpleDataObject(1, "c")

    assert left == right
