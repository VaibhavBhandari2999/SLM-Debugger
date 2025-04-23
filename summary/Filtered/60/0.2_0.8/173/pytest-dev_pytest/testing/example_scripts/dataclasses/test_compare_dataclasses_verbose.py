from dataclasses import dataclass
from dataclasses import field


def test_dataclasses_verbose():
    """
    Function: test_dataclasses_verbose
    
    This function tests the equality of two instances of a dataclass, SimpleDataObject, which contains two fields: field_a and field_b. The function demonstrates the behavior of the dataclass when comparing instances with different values for field_b but the same value for field_a.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Key Points:
    - The dataclass SimpleDataObject is defined with two fields: field_a and field_b.
    - Two instances of SimpleData
    """

    @dataclass
    class SimpleDataObject:
        field_a: int = field()
        field_b: int = field()

    left = SimpleDataObject(1, "b")
    right = SimpleDataObject(1, "c")

    assert left == right
