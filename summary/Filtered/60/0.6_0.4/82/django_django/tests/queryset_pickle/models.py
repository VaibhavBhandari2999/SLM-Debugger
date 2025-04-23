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
        Summary:
        This function is a custom implementation of the `__getstate__` method, which is used to prepare an object's state for pickling. It extends the functionality of the base class's `__getstate__` method by adding a specific version key to the state dictionary.
        
        Parameters:
        - No explicit parameters are passed to this function. It relies on the state dictionary returned by the base class's `__getstate__` method.
        
        Returns:
        - A dictionary containing the state of
        """

        state = super().__getstate__()
        state[DJANGO_VERSION_PICKLE_KEY] = '1.0'
        return state


class MissingDjangoVersionQuerySet(models.QuerySet):
    def __getstate__(self):
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
