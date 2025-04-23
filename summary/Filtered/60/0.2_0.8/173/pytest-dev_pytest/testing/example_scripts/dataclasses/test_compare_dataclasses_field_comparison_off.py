from dataclasses import dataclass
from dataclasses import field


def test_dataclasses_with_attribute_comparison_off():
    """
    This function demonstrates the use of dataclasses in Python, specifically focusing on attribute comparison. It defines a data class `SimpleDataObject` with two fields: `field_a` and `field_b`. The `field_b` is marked with `compare=False`, meaning it will not be used in the comparison operations (`==`, `!=`, etc.). The function creates two instances of `SimpleDataObject` with the same value for `field_a` but different values for `field_b`. Despite the
    """

    @dataclass
    class SimpleDataObject:
        field_a: int = field()
        field_b: int = field(compare=False)

    left = SimpleDataObject(1, "b")
    right = SimpleDataObject(1, "c")

    assert left == right
