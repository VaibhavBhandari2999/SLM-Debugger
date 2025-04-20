from dataclasses import dataclass
from dataclasses import field


def test_comparing_two_different_data_classes():
    """
    Compare two different data classes for inequality.
    
    This function demonstrates the comparison of two different data classes, each with the same field names but different class names. The comparison is expected to return True since the classes are different, even though the fields have the same names and values.
    
    Parameters:
    left (SimpleDataObjectOne): An instance of the first data class.
    right (SimpleDataObjectTwo): An instance of the second data class.
    
    Returns:
    bool: True if the instances are not equal
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
