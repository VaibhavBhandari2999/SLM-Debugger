from dataclasses import dataclass
from dataclasses import field


def test_dataclasses_verbose():
    """
    This function demonstrates the usage of the `dataclass` decorator from the `dataclasses` module to create a simple data class named `SimpleDataObject`. The class has two fields: `field_a` and `field_b`, both of which are integers. The function creates two instances of `SimpleDataObject` with different values for `field_b` but the same value for `field_a`. It then checks if these two instances are equal, which is expected to return `False` because the
    """

    @dataclass
    class SimpleDataObject(object):
        field_a: int = field()
        field_b: int = field()

    left = SimpleDataObject(1, "b")
    right = SimpleDataObject(1, "c")

    assert left == right
