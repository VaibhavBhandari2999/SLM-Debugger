from dataclasses import dataclass
from dataclasses import field


def test_dataclasses_verbose():
    """
    Generate a Python docstring for the provided function.
    
    This function defines a simple data class `SimpleDataObject` with two fields, `field_a` and `field_b`. The function creates two instances of this class with different values for `field_b` but the same value for `field_a`. It then checks if these two instances are equal.
    
    Key Parameters:
    - None
    
    Keywords:
    - None
    
    Input:
    - None
    
    Output:
    - The function does not return any value. It performs an
    """

    @dataclass
    class SimpleDataObject:
        field_a: int = field()
        field_b: int = field()

    left = SimpleDataObject(1, "b")
    right = SimpleDataObject(1, "c")

    assert left == right
