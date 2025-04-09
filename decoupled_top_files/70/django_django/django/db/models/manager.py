"""
This Python file contains definitions for custom Django model managers. It introduces a `BaseManager` class that provides a foundation for creating custom managers, including methods for generating additional methods from a queryset class, managing database queries, and handling serialization for migrations. The `Manager` class extends `BaseManager` and serves as a default manager for Django models. Additionally, the file includes a `ManagerDescriptor` class for managing access to these managers within model instances and an `EmptyManager` subclass that returns an empty queryset.

Key functionalities include:
- Creating and customizing model managers.
- Generating methods from queryset classes.
- Handling database queries and connections.
- Managing serialization for migration purposes.

The `BaseManager` and `Manager` classes interact by inheriting from
"""
import copy
import inspect
from importlib import import_module

from django.db import router
from django.db.models.query import QuerySet


class BaseManager:
    # To retain order, track each time a Manager instance is created.
    creation_counter = 0

    # Set to True for the 'objects' managers that are automatically created.
    auto_created = False

    #: If set to True the manager will be serialized into migrations and will
    #: thus be available in e.g. RunPython operations.
    use_in_migrations = False

    def __new__(cls, *args, **kwargs):
        """
        Create a new instance of the class.
        
        Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
        
        Returns:
        An instance of the class.
        
        Attributes:
        _constructor_args: A tuple containing the arguments passed to the constructor.
        """

        # Capture the arguments to make returning them trivial.
        obj = super().__new__(cls)
        obj._constructor_args = (args, kwargs)
        return obj

    def __init__(self):
        """
        Initializes an instance of the class.
        
        This method sets up the initial state of the object by calling the superclass's `__init__` method, setting a creation counter, initializing the model, name, database connection (`_db`), and hints dictionary.
        
        Attributes:
        model (object): The model associated with the instance.
        name (str): The name of the instance.
        _db (object): The database connection object.
        _hints (dict): A dictionary containing hints
        """

        super().__init__()
        self._set_creation_counter()
        self.model = None
        self.name = None
        self._db = None
        self._hints = {}

    def __str__(self):
        """Return "app_label.model_label.manager_name"."""
        return '%s.%s' % (self.model._meta.label, self.name)

    def __class_getitem__(cls, *args, **kwargs):
        return cls

    def deconstruct(self):
        """
        Return a 5-tuple of the form (as_manager (True), manager_class,
        queryset_class, args, kwargs).

        Raise a ValueError if the manager is dynamically generated.
        """
        qs_class = self._queryset_class
        if getattr(self, '_built_with_as_manager', False):
            # using MyQuerySet.as_manager()
            return (
                True,  # as_manager
                None,  # manager_class
                '%s.%s' % (qs_class.__module__, qs_class.__name__),  # qs_class
                None,  # args
                None,  # kwargs
            )
        else:
            module_name = self.__module__
            name = self.__class__.__name__
            # Make sure it's actually there and not an inner class
            module = import_module(module_name)
            if not hasattr(module, name):
                raise ValueError(
                    "Could not find manager %s in %s.\n"
                    "Please note that you need to inherit from managers you "
                    "dynamically generated with 'from_queryset()'."
                    % (name, module_name)
                )
            return (
                False,  # as_manager
                '%s.%s' % (module_name, name),  # manager_class
                None,  # qs_class
                self._constructor_args[0],  # args
                self._constructor_args[1],  # kwargs
            )

    def check(self, **kwargs):
        return []

    @classmethod
    def _get_queryset_methods(cls, queryset_class):
        """
        This function generates additional methods for a Django model manager based on the provided queryset class. It iterates over the functions defined in the queryset class, filters out private methods and methods marked with `queryset_only=True`, and creates corresponding methods in the manager that delegate to the queryset's methods.
        
        Args:
        cls: The Django model manager class.
        queryset_class: The Django queryset class from which methods are copied.
        
        Returns:
        A dictionary of new methods added to the manager, where each
        """

        def create_method(name, method):
            """
            Generates a method that wraps another method on the queryset. The generated method will call the specified method on the queryset and return its result. The generated method will have the same name and documentation as the original method.
            
            Args:
            name (str): The name of the method to be called on the queryset.
            method (function): The original method to be wrapped.
            
            Returns:
            function: A new method that wraps the specified method on the queryset.
            """

            def manager_method(self, *args, **kwargs):
                return getattr(self.get_queryset(), name)(*args, **kwargs)
            manager_method.__name__ = method.__name__
            manager_method.__doc__ = method.__doc__
            return manager_method

        new_methods = {}
        for name, method in inspect.getmembers(queryset_class, predicate=inspect.isfunction):
            # Only copy missing methods.
            if hasattr(cls, name):
                continue
            # Only copy public methods or methods with the attribute `queryset_only=False`.
            queryset_only = getattr(method, 'queryset_only', None)
            if queryset_only or (queryset_only is None and name.startswith('_')):
                continue
            # Copy the method onto the manager.
            new_methods[name] = create_method(name, method)
        return new_methods

    @classmethod
    def from_queryset(cls, queryset_class, class_name=None):
        """
        Generates a new class based on the given `cls` and `queryset_class`. The generated class will have a `_queryset_class` attribute set to the provided `queryset_class`, and it will inherit from `cls`. Additionally, it will include all the queryset methods defined in `cls` using the `_get_queryset_methods` method.
        
        Args:
        cls (type): The base class to inherit from.
        queryset_class (type): The queryset class to associate with the generated class
        """

        if class_name is None:
            class_name = '%sFrom%s' % (cls.__name__, queryset_class.__name__)
        return type(class_name, (cls,), {
            '_queryset_class': queryset_class,
            **cls._get_queryset_methods(queryset_class),
        })

    def contribute_to_class(self, cls, name):
        """
        Adds a manager to the given model class. Sets the name of the manager and associates it with the model. Creates a descriptor for the manager and adds it to the model's attributes. Also adds the manager to the model's metadata.
        
        Args:
        cls (type): The model class to which the manager will be added.
        name (str): The name of the manager attribute in the model class.
        
        Returns:
        None
        """

        self.name = self.name or name
        self.model = cls

        setattr(cls, name, ManagerDescriptor(self))

        cls._meta.add_manager(self)

    def _set_creation_counter(self):
        """
        Set the creation counter value for this instance and increment the
        class-level copy.
        """
        self.creation_counter = BaseManager.creation_counter
        BaseManager.creation_counter += 1

    def db_manager(self, using=None, hints=None):
        """
        Generates a new database manager instance with the specified database alias and query hints.
        
        Args:
        using (str, optional): The database alias to use for the new instance. Defaults to None, which means the current database alias is retained.
        hints (dict, optional): Query hints to be applied to the new instance. Defaults to None, which means the current hints are retained.
        
        Returns:
        object: A new database manager instance with the specified database alias and query hints.
        """

        obj = copy.copy(self)
        obj._db = using or self._db
        obj._hints = hints or self._hints
        return obj

    @property
    def db(self):
        return self._db or router.db_for_read(self.model, **self._hints)

    #######################
    # PROXIES TO QUERYSET #
    #######################

    def get_queryset(self):
        """
        Return a new QuerySet object. Subclasses can override this method to
        customize the behavior of the Manager.
        """
        return self._queryset_class(model=self.model, using=self._db, hints=self._hints)

    def all(self):
        """
        Retrieve all objects from the related model. This method returns a QuerySet containing all instances of the related model that are associated with the current manager. It does not create a new queryset but rather returns the existing one, ensuring that any previously applied prefetch_related lookups are preserved.
        
        Returns:
        QuerySet: A QuerySet of all related model instances.
        """

        # We can't proxy this method through the `QuerySet` like we do for the
        # rest of the `QuerySet` methods. This is because `QuerySet.all()`
        # works by creating a "copy" of the current queryset and in making said
        # copy, all the cached `prefetch_related` lookups are lost. See the
        # implementation of `RelatedManager.get_queryset()` for a better
        # understanding of how this comes into play.
        return self.get_queryset()

    def __eq__(self, other):
        """
        Check if two instances of the same class are equal based on their constructor arguments.
        
        Args:
        other (object): The object to compare with.
        
        Returns:
        bool: True if both instances have the same class type and constructor arguments, False otherwise.
        """

        return (
            isinstance(other, self.__class__) and
            self._constructor_args == other._constructor_args
        )

    def __hash__(self):
        return id(self)


class Manager(BaseManager.from_queryset(QuerySet)):
    pass


class ManagerDescriptor:

    def __init__(self, manager):
        self.manager = manager

    def __get__(self, instance, cls=None):
        """
        Retrieve the specified manager for the given model class.
        
        Args:
        instance (object): The instance of the model class.
        cls (class): The model class.
        
        Raises:
        AttributeError: If the manager is not accessible via the instance or if the model class is abstract, swapped, or does not have the specified manager.
        
        Returns:
        object: The specified manager for the given model class.
        """

        if instance is not None:
            raise AttributeError("Manager isn't accessible via %s instances" % cls.__name__)

        if cls._meta.abstract:
            raise AttributeError("Manager isn't available; %s is abstract" % (
                cls._meta.object_name,
            ))

        if cls._meta.swapped:
            raise AttributeError(
                "Manager isn't available; '%s' has been swapped for '%s'" % (
                    cls._meta.label,
                    cls._meta.swapped,
                )
            )

        return cls._meta.managers_map[self.manager.name]


class EmptyManager(Manager):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def get_queryset(self):
        return super().get_queryset().none()
