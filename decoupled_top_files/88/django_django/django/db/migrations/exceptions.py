"""
The provided Python file contains a collection of custom exception classes used within a Django application for handling various errors related to database migrations. Each exception class is designed to capture specific issues that may arise during the migration process, such as ambiguities, inconsistencies, and circular dependencies.

#### Classes Defined:
1. **AmbiguityError**: Raised when more than one migration matches a given name prefix.
2. **BadMigrationError**: Raised when a migration is unreadable or has a bad format.
3. **CircularDependencyError**: Raised when there is an impossible-to-resolve circular dependency among migrations.
4. **InconsistentMigrationHistory**: Raised when an applied migration has some of its dependencies not applied.
5. **InvalidBasesError**: Raised when a
"""
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
        Initialize a new instance of the class.
        
        Args:
        message (str): The message associated with this instance.
        node (Node): The node object associated with this instance.
        origin (Node, optional): The origin node of the message. Defaults to None.
        
        Attributes:
        message (str): The message associated with this instance.
        origin (Node): The origin node of the message.
        node (Node): The node object associated with this instance.
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
