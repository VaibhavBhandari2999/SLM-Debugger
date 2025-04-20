from django.db.migrations.operations.base import Operation


class TestOperation(Operation):
    def __init__(self):
        pass

    def deconstruct(self):
        """
        Deconstructs the current object into its class name, an empty list, and an empty dictionary.
        
        This method is used to break down the object into its fundamental components, specifically its class name, and empty lists and dictionaries for attributes and keyword arguments.
        
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
