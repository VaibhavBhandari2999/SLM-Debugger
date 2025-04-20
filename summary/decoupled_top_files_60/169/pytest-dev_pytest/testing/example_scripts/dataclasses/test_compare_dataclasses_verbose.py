from dataclasses import dataclass
from dataclasses import field


def test_dataclasses_verbose():
    """
    Function: test_dataclasses_verbose
    
    This function tests the equality of two instances of a dataclass, SimpleDataObject, which has two fields: field_a and field_b. Both fields are initialized with default values using the `field()` function from the `dataclasses` module.
    
    Parameters:
    - No explicit parameters are required for this function.
    
    Returns:
    - The function does not return any value. It asserts whether the two instances of SimpleDataObject are equal based on their field values.
    
    Note:
    """

    @dataclass
    class SimpleDataObject(object):
        field_a: int = field()
        field_b: int = field()

    left = SimpleDataObject(1, "b")
    right = SimpleDataObject(1, "c")

    assert left == right
