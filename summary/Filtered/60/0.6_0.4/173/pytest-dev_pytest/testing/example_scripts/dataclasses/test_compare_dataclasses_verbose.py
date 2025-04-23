from dataclasses import dataclass
from dataclasses import field


def test_dataclasses_verbose():
    """
    Function: test_dataclasses_verbose
    Summary: This function tests the equality of two instances of a dataclass, SimpleDataObject, which contains two fields, field_a and field_b. The function creates two instances of SimpleDataObject with the same value for field_a but different values for field_b. The function asserts that these two instances are equal.
    
    Parameters:
    - No explicit parameters are required for this function.
    
    Keywords:
    - No specific keywords are used in this function.
    
    Input:
    - Two instances
    """

    @dataclass
    class SimpleDataObject:
        field_a: int = field()
        field_b: int = field()

    left = SimpleDataObject(1, "b")
    right = SimpleDataObject(1, "c")

    assert left == right
