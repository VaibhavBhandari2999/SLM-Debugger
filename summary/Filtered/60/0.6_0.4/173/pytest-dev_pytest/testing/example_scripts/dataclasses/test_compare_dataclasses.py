from dataclasses import dataclass
from dataclasses import field


def test_dataclasses():
    """
    This function demonstrates the usage of dataclasses in Python. It defines a simple data class `SimpleDataObject` with two fields, `field_a` and `field_b`. Both fields are initialized with default values. The function creates two instances of `SimpleDataObject` with the same `field_a` value but different `field_b` values. Despite the difference in `field_b`, the function asserts that the two instances are equal, which is unexpected behavior due to the incorrect type for `field
    """

    @dataclass
    class SimpleDataObject:
        field_a: int = field()
        field_b: int = field()

    left = SimpleDataObject(1, "b")
    right = SimpleDataObject(1, "c")

    assert left == right
