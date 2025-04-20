from dataclasses import dataclass
from dataclasses import field


def test_dataclasses_with_attribute_comparison_off():
    """
    Function: test_dataclasses_with_attribute_comparison_off
    Summary: This function tests the behavior of dataclasses in Python when the attribute comparison is turned off for one of the fields.
    Parameters: None
    Keywords:
    - field_a: An integer field that is included in the comparison.
    - field_b: An integer field that is excluded from the comparison due to the `compare=False` parameter.
    Output: The function asserts that two instances of the `SimpleDataObject` class are equal,
    """

    @dataclass
    class SimpleDataObject:
        field_a: int = field()
        field_b: int = field(compare=False)

    left = SimpleDataObject(1, "b")
    right = SimpleDataObject(1, "c")

    assert left == right
