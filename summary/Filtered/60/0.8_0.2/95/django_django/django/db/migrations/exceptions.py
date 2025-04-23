from django.db import DatabaseError


class AmbiguityError(Exception):
    """More than one migration matches a name prefix."""

    pass


class BadMigrationError(Exception):
    """There's a bad migration (unreadable/bad format/etc.)."""

    pass


class CircularDependencyError(Exception):
    """There's an impossible-to-resolve circular dependency."""

    pass


class InconsistentMigrationHistory(Exception):
    """An applied migration has some of its dependencies not applied."""

    pass


class InvalidBasesError(ValueError):
    """A model's base classes can't be resolved."""

    pass


class IrreversibleError(RuntimeError):
    """An irreversible migration is about to be reversed."""

    pass


class NodeNotFoundError(LookupError):
    """An attempt on a node is made that is not available in the graph."""

    def __init__(self, message, node, origin=None):
        """
        Initialize a new instance of a custom exception.
        
        Args:
        message (str): The error message to be associated with the exception.
        node (object): The node object related to the error.
        origin (object, optional): The origin object from which the exception originated. Defaults to None.
        
        Returns:
        None: This function does not return any value. It is used to raise an exception.
        """

        self.message = message
        self.origin = origin
        self.node = node

    def __str__(self):
        return self.message

    def __repr__(self):
        return "NodeNotFoundError(%r)" % (self.node,)


class MigrationSchemaMissing(DatabaseError):
    pass


class InvalidMigrationPlan(ValueError):
    pass
