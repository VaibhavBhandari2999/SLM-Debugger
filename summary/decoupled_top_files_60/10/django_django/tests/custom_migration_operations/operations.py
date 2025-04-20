from django.db.migrations.operations.base import Operation


class TestOperation(Operation):
    def __init__(self):
        pass

    def deconstruct(self):
        """
        Deconstructs the current object into its class name, an empty list, and an empty dictionary.
        
        This method is used to break down the object into its fundamental components, specifically its class name, and two empty collections (a list and a dictionary).
        
        Returns:
        tuple: A tuple containing the class name (str), an empty list (list), and an empty dictionary (dict).
        """

        return (
            self.__class__.__name__,
            [],
            {}
        )

    @property
    def reversible(self):
        return True

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        pass

    def state_backwards(self, app_label, state):
        pass

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        pass


class CreateModel(TestOperation):
    pass


class ArgsOperation(TestOperation):
    def __init__(self, arg1, arg2):
        self.arg1, self.arg2 = arg1, arg2

    def deconstruct(self):
        return (
            self.__class__.__name__,
            [self.arg1, self.arg2],
            {}
        )


class KwargsOperation(TestOperation):
    def __init__(self, kwarg1=None, kwarg2=None):
        self.kwarg1, self.kwarg2 = kwarg1, kwarg2

    def deconstruct(self):
        """
        Deconstructs the object into its class name, arguments, and keyword arguments.
        
        This function is used to break down the object into its essential components for serialization or logging purposes.
        
        Args:
        None (all parameters are internal to the class)
        
        Returns:
        tuple: A tuple containing the class name, a list of positional arguments (empty in this case), and a dictionary of keyword arguments.
        
        Example:
        >>> obj = SomeClass(kwarg1='value1', kwarg2='value2
        """

        kwargs = {}
        if self.kwarg1 is not None:
            kwargs['kwarg1'] = self.kwarg1
        if self.kwarg2 is not None:
            kwargs['kwarg2'] = self.kwarg2
        return (
            self.__class__.__name__,
            [],
            kwargs
        )


class ArgsKwargsOperation(TestOperation):
    def __init__(self, arg1, arg2, kwarg1=None, kwarg2=None):
        self.arg1, self.arg2 = arg1, arg2
        self.kwarg1, self.kwarg2 = kwarg1, kwarg2

    def deconstruct(self):
        """
        Deconstructs the object into a tuple containing the class name, positional arguments, and keyword arguments.
        
        Args:
        self (object): The instance of the class to be deconstructed.
        
        Returns:
        tuple: A tuple containing:
        - str: The class name of the object.
        - list: A list of positional arguments.
        - dict: A dictionary of keyword arguments.
        
        This method extracts the class name, positional arguments (arg1, arg2), and keyword arguments (kwarg1
        """

        kwargs = {}
        if self.kwarg1 is not None:
            kwargs['kwarg1'] = self.kwarg1
        if self.kwarg2 is not None:
            kwargs['kwarg2'] = self.kwarg2
        return (
            self.__class__.__name__,
            [self.arg1, self.arg2],
            kwargs,
        )


class ExpandArgsOperation(TestOperation):
    serialization_expand_args = ['arg']

    def __init__(self, arg):
        self.arg = arg

    def deconstruct(self):
        return (
            self.__class__.__name__,
            [self.arg],
            {}
        )
