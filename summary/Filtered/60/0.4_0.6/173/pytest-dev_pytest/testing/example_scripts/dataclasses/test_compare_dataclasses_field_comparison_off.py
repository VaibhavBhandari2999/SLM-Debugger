from dataclasses import dataclass
from dataclasses import field


def test_dataclasses_with_attribute_comparison_off():
    """
    Function to test dataclasses with attribute comparison off.
    
    This function demonstrates the usage of the `dataclass` decorator from the `dataclasses` module in Python. It creates a simple data class `SimpleDataObject` with two fields: `field_a` and `field_b`. The `field_b` is marked with `compare=False` to disable comparison based on this field.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - `field_a`: An integer field used for
    """

    @dataclass
    class SimpleDataObject:
        field_a: int = field()
        field_b: int = field(compare=False)

    left = SimpleDataObject(1, "b")
    right = SimpleDataObject(1, "c")

    assert left == right
