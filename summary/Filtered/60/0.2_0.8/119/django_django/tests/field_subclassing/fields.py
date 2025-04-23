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
        Count the number of times a field is accessed for a given instance.
        
        This function increments the access count for a field on a given instance. It uses a private attribute to store the count.
        
        Parameters:
        instance (object): The instance of the model or object whose field access count is to be incremented.
        get_or_set (str): A string indicating whether the access is for 'get' or 'set' operations.
        
        Returns:
        None: This function does not return any value. It modifies
        """

        count_attr = "_%s_%s_count" % (self.field.attname, get_or_set)
        count = getattr(instance, count_attr, 0)
        setattr(instance, count_attr, count + 1)


class CustomDescriptorField(models.CharField):
    descriptor_class = CustomDeferredAttribute
