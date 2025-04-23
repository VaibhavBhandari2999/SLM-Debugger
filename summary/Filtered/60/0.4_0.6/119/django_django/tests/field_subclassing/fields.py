from django.db import models
from django.db.models.query_utils import DeferredAttribute


class CustomTypedField(models.TextField):
    def db_type(self, connection):
        return "custom_field"


class CustomDeferredAttribute(DeferredAttribute):
    def __get__(self, instance, cls=None):
        self._count_call(instance, "get")
        return super().__get__(instance, cls)

    def __set__(self, instance, value):
        self._count_call(instance, "set")
        instance.__dict__[self.field.attname] = value

    def _count_call(self, instance, get_or_set):
        """
        Counts the number of times a field is accessed (either 'get' or 'set') for a given instance.
        
        Parameters:
        instance (object): The instance of the model for which the count is being tracked.
        get_or_set (str): A string indicating whether the access is a 'get' or 'set' operation.
        
        Returns:
        int: The updated count of the number of times the field has been accessed.
        
        This function increments a count attribute for each access to a specific
        """

        count_attr = "_%s_%s_count" % (self.field.attname, get_or_set)
        count = getattr(instance, count_attr, 0)
        setattr(instance, count_attr, count + 1)


class CustomDescriptorField(models.CharField):
    descriptor_class = CustomDeferredAttribute
