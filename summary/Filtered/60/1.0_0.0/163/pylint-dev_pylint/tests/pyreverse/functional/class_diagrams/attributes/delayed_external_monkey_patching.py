from _monkey import Monkey


class Tree:
    def __init__(self):
        """
        Initialize a new instance of the class.
        
        This method sets up the initial state of the object.
        
        Parameters:
        None
        
        Attributes:
        number_of_bananas (int): The initial number of bananas, set to 5.
        inhabitant (Monkey): The inhabitant of the object, which is an instance of the Monkey class with the name 'Steve'.
        
        Returns:
        None
        
        Notes:
        - The `inhabitant` attribute is an instance of the `Monkey` class with the
        """

        self.number_of_bananas = 5
        self.inhabitant = Monkey(
            "Steve"
        )  # This will trigger the evaluation of `monkey.py`
