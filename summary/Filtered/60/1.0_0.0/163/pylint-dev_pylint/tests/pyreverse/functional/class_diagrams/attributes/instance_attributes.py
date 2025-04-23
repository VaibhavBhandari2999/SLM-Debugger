class InstanceAttributes:
    def __init__(self):
        """
        Initialize the object with default values.
        
        This method sets up the object with initial values for its attributes.
        
        Attributes:
        my_int_without_type_hint (int): An integer without type hint.
        my_int_with_type_hint (int): An integer with type hint.
        my_optional_int (int, optional): An optional integer. Defaults to None.
        """

        self.my_int_without_type_hint = 1
        self.my_int_with_type_hint: int = 2
        self.my_optional_int: int = None
