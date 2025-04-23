from dataclasses import dataclass
from dataclasses import field


def test_dataclasses_verbose():
    """
    Function: test_dataclasses_verbose
    
    This function tests the behavior of a dataclass with two fields, 'field_a' and 'field_b', both of type int. The function creates two instances of the dataclass, 'left' and 'right', with the same value for 'field_a' but different values for 'field_b'. The function then checks if these two instances are considered equal.
    
    Parameters:
    - No explicit parameters are required for this function.
    
    Returns:
    - The function does not
    """

    @dataclass
    class SimpleDataObject:
        field_a: int = field()
        field_b: int = field()

    left = SimpleDataObject(1, "b")
    right = SimpleDataObject(1, "c")

    assert left == right
