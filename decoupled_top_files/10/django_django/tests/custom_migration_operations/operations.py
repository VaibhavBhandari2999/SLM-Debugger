from django.db.migrations.operations.base import Operation


class TestOperation(Operation):
    def __init__(self):
        pass

    def deconstruct(self):
        """
        deconstruct() -> tuple
        Returns a tuple containing the class name, an empty list, and an empty dictionary.
        
        Args:
        None
        
        Returns:
        tuple: A tuple with three elements:
        - str: The class name of the object being deconstructed.
        - list: An empty list ([])
        - dict: An empty dictionary ({})
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
        """
        Deconstructs the object into its class name, arguments, and keyword arguments.
        
        Args:
        None
        
        Returns:
        A tuple containing:
        - The class name of the object (str)
        - A list of positional arguments (list)
        - An empty dictionary of keyword arguments (dict)
        """

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
        
        Args:
        None
        
        Returns:
        tuple: A tuple containing the class name (str), an empty list of positional arguments, and a dictionary of keyword arguments.
        
        Keyword Arguments:
        kwarg1: The first keyword argument (if not None).
        kwarg2: The second keyword argument (if not None).
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
        Deconstructs an instance into its class name, arguments, and keyword arguments.
        
        Args:
        self: The instance of the class to be deconstructed.
        
        Returns:
        A tuple containing:
        - The class name (str)
        - A list of positional arguments ([arg1, arg2])
        - A dictionary of keyword arguments ({'kwarg1': value, 'kwarg2': value})
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
        """
        Deconstructs the object into its class name, arguments, and keyword arguments.
        
        Args:
        None
        
        Returns:
        A tuple containing:
        - The class name of the object (str)
        - A list of positional arguments (list)
        - A dictionary of keyword arguments (dict)
        """

        return (
            self.__class__.__name__,
            [self.arg],
            {}
        )
