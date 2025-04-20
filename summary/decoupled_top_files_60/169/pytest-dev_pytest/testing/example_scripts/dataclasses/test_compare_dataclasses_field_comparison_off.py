from dataclasses import dataclass
from dataclasses import field


def test_dataclasses_with_attribute_comparison_off():
    """
    This function tests the behavior of dataclasses in Python, specifically focusing on attribute comparison. It defines a dataclass `SimpleDataObject` with two fields, `field_a` and `field_b`. The `field_b` is marked with `compare=False`, which means it will not be used in the comparison of instances of `SimpleDataObject`. The function creates two instances of `SimpleDataObject` with the same value for `field_a` but different values for `field_b`. It then
    """

    @dataclass
    class SimpleDataObject(object):
        field_a: int = field()
        field_b: int = field(compare=False)

    left = SimpleDataObject(1, "b")
    right = SimpleDataObject(1, "c")

    assert left == right
