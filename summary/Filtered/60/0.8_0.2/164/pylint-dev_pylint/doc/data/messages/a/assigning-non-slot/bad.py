class Student:
    __slots__ = ('name',)

    def __init__(self, name, surname):
        """
        Initialize a new instance of the class.
        
        Args:
        name (str): The first name of the person.
        surname (str): The surname of the person.
        
        Returns:
        None: This method does not return any value. It sets up the instance variables for the object.
        
        Note:
        This method assigns the provided name and surname to the respective instance variables and then calls the `setup` method.
        """

        self.name = name
        self.surname = surname  # [assigning-non-slot]
        self.setup()

    def setup(self):
        pass
