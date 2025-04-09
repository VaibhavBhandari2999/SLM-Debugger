"""
This Python file contains definitions for several Django models and utility functions. It demonstrates various aspects of Django model management, including custom queryset methods for handling pickling, foreign key relationships, and abstract base classes.

#### Classes Defined:
1. **Numbers**: Contains a static method `get_static_number()` which returns the integer value 2.
2. **PreviousDjangoVersionQuerySet**: A custom queryset manager that adds Django version information to its pickled state.
3. **MissingDjangoVersionQuerySet**: A custom queryset manager that removes Django version information from its pickled state.
4. **Group**: A Django model representing a group with fields for name and related objects using custom managers.
5. **Event**: A Django model representing an event with
"""
import datetime

from django.db import DJANGO_VERSION_PICKLE_KEY, models
from django.utils.translation import gettext_lazy as _


def standalone_number():
    return 1


class Numbers:
    @staticmethod
    def get_static_number():
        return 2


class PreviousDjangoVersionQuerySet(models.QuerySet):
    def __getstate__(self):
        """
        Get the state of the object for pickling.
        
        This method overrides the default `__getstate__` method by adding
        Django version information to the state dictionary. The state is
        returned as a modified dictionary containing the original state
        along with the Django version key set to '1.0'.
        
        Args:
        None
        
        Returns:
        dict: A dictionary containing the original state and the Django version key.
        """

        state = super().__getstate__()
        state[DJANGO_VERSION_PICKLE_KEY] = '1.0'
        return state


class MissingDjangoVersionQuerySet(models.QuerySet):
    def __getstate__(self):
        """
        Get the state of the object for pickling.
        
        This method overrides the default behavior by removing the Django version
        pickle key from the state dictionary before returning it.
        
        Args:
        None
        
        Returns:
        dict: The state of the object with the Django version key removed.
        """

        state = super().__getstate__()
        del state[DJANGO_VERSION_PICKLE_KEY]
        return state


class Group(models.Model):
    name = models.CharField(_('name'), max_length=100)
    objects = models.Manager()
    previous_django_version_objects = PreviousDjangoVersionQuerySet.as_manager()
    missing_django_version_objects = MissingDjangoVersionQuerySet.as_manager()


class Event(models.Model):
    title = models.CharField(max_length=100)
    group = models.ForeignKey(Group, models.CASCADE, limit_choices_to=models.Q())


class Happening(models.Model):
    when = models.DateTimeField(blank=True, default=datetime.datetime.now)
    name = models.CharField(blank=True, max_length=100, default="test")
    number1 = models.IntegerField(blank=True, default=standalone_number)
    number2 = models.IntegerField(blank=True, default=Numbers.get_static_number)
    event = models.OneToOneField(Event, models.CASCADE, null=True)


class Container:
    # To test pickling we need a class that isn't defined on module, but
    # is still available from app-cache. So, the Container class moves
    # SomeModel outside of module level
    class SomeModel(models.Model):
        somefield = models.IntegerField()


class M2MModel(models.Model):
    added = models.DateField(default=datetime.date.today)
    groups = models.ManyToManyField(Group)


class AbstractEvent(Event):
    class Meta:
        abstract = True
        ordering = ['title']


class MyEvent(AbstractEvent):
    pass


class Edition(models.Model):
    event = models.ForeignKey('MyEvent', on_delete=models.CASCADE)
