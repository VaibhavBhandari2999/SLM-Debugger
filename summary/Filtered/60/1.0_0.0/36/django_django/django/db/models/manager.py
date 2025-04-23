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
        This function is a custom `__new__` method for a class. It is responsible for creating a new instance of the class.
        
        Parameters:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
        
        Returns:
        obj: An instance of the class.
        
        The function captures the arguments and keyword arguments passed during the instantiation and stores them in the `_constructor_args` attribute of the newly created object.
        """

        # Capture the arguments to make returning them trivial.
        obj = super().__new__(cls)
        obj._constructor_args = (args, kwargs)
        return obj

    def __init__(self):
        super().__init__()
        self._set_creation_counter()
        self.model = None
        self.name = None
        self._db = None
        self._hints = {}

    def __str__(self):
        """Return "app_label.model_label.manager_name"."""
        return '%s.%s' % (self.model._meta.label, self.name)

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
        def create_method(name, method):
            """
            Generates a method to be used as a manager method for a Django model queryset.
            
            This function takes a name and a method as input and returns a new method that can be used as a manager method for a Django model queryset. The returned method will call the provided method on the queryset obtained from the manager.
            
            Parameters:
            name (str): The name of the method to be called on the queryset.
            method (function): The method to be called on the queryset.
            
            Returns:
            function:
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
        if class_name is None:
            class_name = '%sFrom%s' % (cls.__name__, queryset_class.__name__)
        return type(class_name, (cls,), {
            '_queryset_class': queryset_class,
            **cls._get_queryset_methods(queryset_class),
        })

    def contribute_to_class(self, model, name):
        """
        This function contributes a custom manager to a Django model.
        
        Parameters:
        model (django.db.models.Model): The Django model to which the custom manager will be added.
        name (str): The name of the attribute on the model that will hold the custom manager.
        
        This function performs the following actions:
        1. Sets the name of the custom manager, using the provided name or the model's name if none is provided.
        2. Attaches the custom manager to the model using a descriptor.
        3.
        """

        self.name = self.name or name
        self.model = model

        setattr(model, name, ManagerDescriptor(self))

        model._meta.add_manager(self)

    def _set_creation_counter(self):
        """
        Set the creation counter value for this instance and increment the
        class-level copy.
        """
        self.creation_counter = BaseManager.creation_counter
        BaseManager.creation_counter += 1

    def db_manager(self, using=None, hints=None):
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
        # We can't proxy this method through the `QuerySet` like we do for the
        # rest of the `QuerySet` methods. This is because `QuerySet.all()`
        # works by creating a "copy" of the current queryset and in making said
        # copy, all the cached `prefetch_related` lookups are lost. See the
        # implementation of `RelatedManager.get_queryset()` for a better
        # understanding of how this comes into play.
        return self.get_queryset()

    def __eq__(self, other):
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
        The `__get__` method is a descriptor method that is used to control access to the manager attribute of a Django model class. It is called when the manager is accessed as an attribute of a model instance or model class.
        
        Parameters:
        - `instance`: The model instance that the manager is being accessed through. If `instance` is not `None`, an `AttributeError` is raised.
        - `cls`: The model class that the manager is being accessed through.
        
        Returns:
        - The manager
        """

        if instance is not None:
            raise AttributeError("Manager isn't accessible via %s instances" % cls.__name__)

        if cls._meta.abstract:
            raise AttributeError("Manager isn't available; %s is abstract" % (
                cls._meta.object_name,
            ))

        if cls._meta.swapped:
            raise AttributeError(
                "Manager isn't available; '%s.%s' has been swapped for '%s'" % (
                    cls._meta.app_label,
                    cls._meta.object_name,
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
er().get_queryset().none()
