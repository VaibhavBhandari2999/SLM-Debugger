from dataclasses import dataclass
from dataclasses import field


def test_dataclasses():
    """
    This function demonstrates the usage of dataclasses in Python. It defines a simple data class `SimpleDataObject` with two fields, `field_a` and `field_b`. Both fields are initialized with default values. The function then creates two instances of `SimpleDataObject` with the same value for `field_a` but different values for `field_b`. Despite the difference in `field_b`, the two instances are considered equal because only `field_a` is used in the equality comparison.
    
    Key
    """

    @dataclass
    class SimpleDataObject:
        field_a: int = field()
        field_b: int = field()

    left = SimpleDataObject(1, "b")
    right = SimpleDataObject(1, "c")

    assert left == right
