from dataclasses import dataclass
from dataclasses import field


def test_comparing_two_different_data_classes():
    """
    Compare two different data classes.
    
    This function demonstrates the comparison of two different data classes, `SimpleDataObjectOne` and `SimpleDataObjectTwo`, which share the same field names but are distinct classes. The comparison is based on the equality of their fields.
    
    Parameters:
    None
    
    Returns:
    bool: Returns `True` if the two data objects are not equal, and `False` otherwise.
    
    Note:
    Even though the two data classes have the same field names, they are considered different
    """

    @dataclass
    class SimpleDataObjectOne:
        field_a: int = field()
        field_b: int = field()

    @dataclass
    class SimpleDataObjectTwo:
        field_a: int = field()
        field_b: int = field()

    left = SimpleDataObjectOne(1, "b")
    right = SimpleDataObjectTwo(1, "c")

    assert left != right
