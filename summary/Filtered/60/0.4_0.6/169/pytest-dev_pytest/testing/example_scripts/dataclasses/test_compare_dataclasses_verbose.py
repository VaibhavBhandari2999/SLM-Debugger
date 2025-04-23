from dataclasses import dataclass
from dataclasses import field


def test_dataclasses_verbose():
    """
    This function tests the behavior of a dataclass with verbose field initialization. The dataclass, `SimpleDataObject`, is defined with two fields, `field_a` and `field_b`, both of type `int`. The function creates two instances of `SimpleDataObject` with the same `field_a` value but different `field_b` values. Despite the difference in `field_b`, the function asserts that the two instances are equal, which may indicate an issue with the field initialization or comparison
    """

    @dataclass
    class SimpleDataObject(object):
        field_a: int = field()
        field_b: int = field()

    left = SimpleDataObject(1, "b")
    right = SimpleDataObject(1, "c")

    assert left == right
