from dataclasses import dataclass
from dataclasses import field


def test_dataclasses_with_attribute_comparison_off():
    """
    This function demonstrates the use of dataclasses in Python, specifically focusing on how to control attribute comparison. The `@dataclass` decorator is used to define a simple data class `SimpleDataObject` with two fields: `field_a` and `field_b`. The `field_b` is marked with `compare=False`, which means it will not be considered during comparison operations.
    
    Key Parameters:
    - `field_a`: An integer field.
    - `field_b`: An integer field, but comparison is
    """

    @dataclass
    class SimpleDataObject:
        field_a: int = field()
        field_b: int = field(compare=False)

    left = SimpleDataObject(1, "b")
    right = SimpleDataObject(1, "c")

    assert left == right
