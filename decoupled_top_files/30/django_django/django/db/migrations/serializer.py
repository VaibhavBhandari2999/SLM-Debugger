import builtins
import collections.abc
import datetime
import decimal
import enum
import functools
import math
import re
import types
import uuid

from django.conf import SettingsReference
from django.db import models
from django.db.migrations.operations.base import Operation
from django.db.migrations.utils import COMPILED_REGEX_TYPE, RegexObject
from django.utils.functional import LazyObject, Promise
from django.utils.timezone import utc
from django.utils.version import get_docs_version


class BaseSerializer:
    def __init__(self, value):
        self.value = value

    def serialize(self):
        raise NotImplementedError('Subclasses of BaseSerializer must implement the serialize() method.')


class BaseSequenceSerializer(BaseSerializer):
    def _format(self):
        raise NotImplementedError('Subclasses of BaseSequenceSerializer must implement the _format() method.')

    def serialize(self):
        """
        Serializes the value of the object into a string representation.
        
        Args:
        None
        
        Returns:
        A tuple containing the serialized string and a set of imported modules.
        
        Summary:
        This function iterates over each item in the value attribute of the object, serializing each item using the appropriate serializer based on its type. It collects all the imported modules required during serialization and formats the final string representation using the `_format` method. The function returns a tuple with the formatted string and the
        """

        imports = set()
        strings = []
        for item in self.value:
            item_string, item_imports = serializer_factory(item).serialize()
            imports.update(item_imports)
            strings.append(item_string)
        value = self._format()
        return value % (", ".join(strings)), imports


class BaseSimpleSerializer(BaseSerializer):
    def serialize(self):
        return repr(self.value), set()


class ChoicesSerializer(BaseSerializer):
    def serialize(self):
        return serializer_factory(self.value.value).serialize()


class DateTimeSerializer(BaseSerializer):
    """For datetime.*, except datetime.datetime."""
    def serialize(self):
        return repr(self.value), {'import datetime'}


class DatetimeDatetimeSerializer(BaseSerializer):
    """For datetime.datetime."""
    def serialize(self):
        """
        Serializes a timezone-aware datetime object to a string representation.
        
        Args:
        value (datetime): The datetime object to be serialized.
        
        Returns:
        tuple: A tuple containing the string representation of the datetime object and a set of required imports.
        
        Summary:
        This function takes a timezone-aware datetime object, converts it to UTC if necessary, and returns its string representation along with the required imports for handling timezone conversions.
        """

        if self.value.tzinfo is not None and self.value.tzinfo != utc:
            self.value = self.value.astimezone(utc)
        imports = ["import datetime"]
        if self.value.tzinfo is not None:
            imports.append("from django.utils.timezone import utc")
        return repr(self.value).replace('<UTC>', 'utc'), set(imports)


class DecimalSerializer(BaseSerializer):
    def serialize(self):
        return repr(self.value), {"from decimal import Decimal"}


class DeconstructableSerializer(BaseSerializer):
    @staticmethod
    def serialize_deconstructed(path, args, kwargs):
        """
        Serialize a deconstructed path, arguments, and keyword arguments.
        
        Args:
        path (str): The path to be serialized.
        args (tuple): A tuple of positional arguments.
        kwargs (dict): A dictionary of keyword arguments.
        
        Returns:
        str: The serialized representation of the deconstructed path, arguments, and keyword arguments.
        dict: A dictionary of imported modules required for deserialization.
        
        Summary:
        This function takes a deconstructed path, arguments, and keyword arguments,
        """

        name, imports = DeconstructableSerializer._serialize_path(path)
        strings = []
        for arg in args:
            arg_string, arg_imports = serializer_factory(arg).serialize()
            strings.append(arg_string)
            imports.update(arg_imports)
        for kw, arg in sorted(kwargs.items()):
            arg_string, arg_imports = serializer_factory(arg).serialize()
            imports.update(arg_imports)
            strings.append("%s=%s" % (kw, arg_string))
        return "%s(%s)" % (name, ", ".join(strings)), imports

    @staticmethod
    def _serialize_path(path):
        """
        Serialize a given path into a module and name tuple.
        
        Args:
        path (str): The fully qualified path of a Django model or field.
        
        Returns:
        tuple: A tuple containing the serialized name and a set of import statements.
        
        Summary:
        This function takes a fully qualified path of a Django model or field and splits it into its module and name components. Depending on the module, it either imports the `models` module from `django.db` or imports the specified module.
        """

        module, name = path.rsplit(".", 1)
        if module == "django.db.models":
            imports = {"from django.db import models"}
            name = "models.%s" % name
        else:
            imports = {"import %s" % module}
            name = path
        return name, imports

    def serialize(self):
        return self.serialize_deconstructed(*self.value.deconstruct())


class DictionarySerializer(BaseSerializer):
    def serialize(self):
        """
        Serialize the dictionary into a string representation.
        
        Args:
        self (dict): The dictionary to be serialized.
        
        Returns:
        tuple: A string representation of the dictionary and a set of imported modules.
        
        Process:
        - Traverse through each key-value pair in the dictionary.
        - For each key, serialize it using the appropriate serializer based on its type.
        - Similarly, serialize each value using the appropriate serializer based on its type.
        - Collect all the imported modules from the serialization process
        """

        imports = set()
        strings = []
        for k, v in sorted(self.value.items()):
            k_string, k_imports = serializer_factory(k).serialize()
            v_string, v_imports = serializer_factory(v).serialize()
            imports.update(k_imports)
            imports.update(v_imports)
            strings.append((k_string, v_string))
        return "{%s}" % (", ".join("%s: %s" % (k, v) for k, v in strings)), imports


class EnumSerializer(BaseSerializer):
    def serialize(self):
        """
        Serialize the enum value to a string representation.
        
        Args:
        None
        
        Returns:
        A tuple containing:
        - A string representation of the serialized enum value in the format: '{module}.{enum_class.__qualname__}[{self.value.name}]'
        - A set of import statements required to deserialize the enum value, which includes 'import {module}'.
        
        Example:
        >>> enum_value = MyEnum.VALUE
        >>> serialize(enum_value)
        ('my_module.MyEnum[
        """

        enum_class = self.value.__class__
        module = enum_class.__module__
        return (
            '%s.%s[%r]' % (module, enum_class.__qualname__, self.value.name),
            {'import %s' % module},
        )


class FloatSerializer(BaseSimpleSerializer):
    def serialize(self):
        """
        Serializes the value of the node.
        
        This method handles special floating-point values such as NaN and infinity by converting them into their string representations using `math.isnan` and `math.isinf`. If the value is either NaN or infinity, it returns a formatted string with the value enclosed in `float()` and an empty set. Otherwise, it calls the `super().serialize()` method to handle the serialization of other types of values.
        
        Args:
        None
        
        Returns:
        A tuple containing
        """

        if math.isnan(self.value) or math.isinf(self.value):
            return 'float("{}")'.format(self.value), set()
        return super().serialize()


class FrozensetSerializer(BaseSequenceSerializer):
    def _format(self):
        return "frozenset([%s])"


class FunctionTypeSerializer(BaseSerializer):
    def serialize(self):
        """
        Generate a Python docstring for the provided function.
        
        Args:
        func (function): The function to generate a docstring for.
        
        Returns:
        str: A formatted docstring summarizing the function's purpose and behavior.
        """

        if getattr(self.value, "__self__", None) and isinstance(self.value.__self__, type):
            klass = self.value.__self__
            module = klass.__module__
            return "%s.%s.%s" % (module, klass.__name__, self.value.__name__), {"import %s" % module}
        # Further error checking
        if self.value.__name__ == '<lambda>':
            raise ValueError("Cannot serialize function: lambda")
        if self.value.__module__ is None:
            raise ValueError("Cannot serialize function %r: No module" % self.value)

        module_name = self.value.__module__

        if '<' not in self.value.__qualname__:  # Qualname can include <locals>
            return '%s.%s' % (module_name, self.value.__qualname__), {'import %s' % self.value.__module__}

        raise ValueError(
            'Could not find function %s in %s.\n' % (self.value.__name__, module_name)
        )


class FunctoolsPartialSerializer(BaseSerializer):
    def serialize(self):
        """
        Serialize a `functools.partial` object.
        
        Args:
        value (functools.partial): The `functools.partial` object to be serialized.
        
        Returns:
        tuple: A tuple containing the serialized string representation of the `functools.partial` object and a set of import statements required for deserialization.
        
        Summary:
        This function serializes a `functools.partial` object by extracting its function, arguments, and keyword arguments. It then constructs a string representation of
        """

        # Serialize functools.partial() arguments
        func_string, func_imports = serializer_factory(self.value.func).serialize()
        args_string, args_imports = serializer_factory(self.value.args).serialize()
        keywords_string, keywords_imports = serializer_factory(self.value.keywords).serialize()
        # Add any imports needed by arguments
        imports = {'import functools', *func_imports, *args_imports, *keywords_imports}
        return (
            'functools.%s(%s, *%s, **%s)' % (
                self.value.__class__.__name__,
                func_string,
                args_string,
                keywords_string,
            ),
            imports,
        )


class IterableSerializer(BaseSerializer):
    def serialize(self):
        """
        Serializes a list of items into a string representation.
        
        Args:
        self: The instance of the class containing the 'value' attribute to be serialized.
        
        Returns:
        A tuple containing the serialized string and a set of imported modules.
        
        Summary:
        This function iterates over each item in the 'value' attribute of the class instance, serializing each item using the appropriate serializer based on its type. It collects all the necessary imports and strings required for serialization. If there are no
        """

        imports = set()
        strings = []
        for item in self.value:
            item_string, item_imports = serializer_factory(item).serialize()
            imports.update(item_imports)
            strings.append(item_string)
        # When len(strings)==0, the empty iterable should be serialized as
        # "()", not "(,)" because (,) is invalid Python syntax.
        value = "(%s)" if len(strings) != 1 else "(%s,)"
        return value % (", ".join(strings)), imports


class ModelFieldSerializer(DeconstructableSerializer):
    def serialize(self):
        attr_name, path, args, kwargs = self.value.deconstruct()
        return self.serialize_deconstructed(path, args, kwargs)


class ModelManagerSerializer(DeconstructableSerializer):
    def serialize(self):
        """
        Serialize a value into a Django queryset.
        
        Args:
        self (DeconstructedValue): The deconstructed value object containing the queryset information.
        
        Returns:
        tuple: A tuple containing the serialized queryset and any required imports.
        
        Summary:
        This function takes a deconstructed value object and serializes it into a Django queryset. It first checks if the value is an instance of a manager and then either returns the serialized manager or calls another function to serialize the deconstructed queryset. The function uses the
        """

        as_manager, manager_path, qs_path, args, kwargs = self.value.deconstruct()
        if as_manager:
            name, imports = self._serialize_path(qs_path)
            return "%s.as_manager()" % name, imports
        else:
            return self.serialize_deconstructed(manager_path, args, kwargs)


class OperationSerializer(BaseSerializer):
    def serialize(self):
        """
        Serialize the given value into a Django migration operation.
        
        Args:
        self (object): The object containing the value to be serialized.
        
        Returns:
        tuple: A tuple containing the serialized string and the required imports.
        
        Important Functions:
        - `OperationWriter`: Used to serialize the value into a Django migration operation.
        - `_write()`: Handles trailing commas in nested operations.
        
        Variables Affected:
        - `string`: The serialized string of the operation.
        - `imports`:
        """

        from django.db.migrations.writer import OperationWriter
        string, imports = OperationWriter(self.value, indentation=0).serialize()
        # Nested operation, trailing comma is handled in upper OperationWriter._write()
        return string.rstrip(','), imports


class RegexSerializer(BaseSerializer):
    def serialize(self):
        """
        Serialize a regular expression pattern and its flags into a Python code string.
        
        Args:
        value (re.Pattern): The regular expression pattern to be serialized.
        
        Returns:
        tuple: A tuple containing the serialized regular expression and the required imports.
        
        Summary:
        This function takes a regular expression pattern and its flags, serializes them into a Python code string using the `re.compile` function, and returns the serialized pattern along with the necessary imports. It also turns off default implicit flags to ensure
        """

        regex_pattern, pattern_imports = serializer_factory(self.value.pattern).serialize()
        # Turn off default implicit flags (e.g. re.U) because regexes with the
        # same implicit and explicit flags aren't equal.
        flags = self.value.flags ^ re.compile('').flags
        regex_flags, flag_imports = serializer_factory(flags).serialize()
        imports = {'import re', *pattern_imports, *flag_imports}
        args = [regex_pattern]
        if flags:
            args.append(regex_flags)
        return "re.compile(%s)" % ', '.join(args), imports


class SequenceSerializer(BaseSequenceSerializer):
    def _format(self):
        return "[%s]"


class SetSerializer(BaseSequenceSerializer):
    def _format(self):
        """
        Formats the given value as a set literal in Python.
        
        Args:
        self: The instance of the class containing the 'value' attribute.
        
        Returns:
        A string representing the set literal or a call to the `set()` constructor based on the value of the 'value' attribute.
        
        Notes:
        - If the 'value' attribute is not empty, the function returns a formatted string with the value enclosed in curly braces `{}`.
        - If the 'value' attribute is empty
        """

        # Serialize as a set literal except when value is empty because {}
        # is an empty dict.
        return '{%s}' if self.value else 'set(%s)'


class SettingsReferenceSerializer(BaseSerializer):
    def serialize(self):
        return "settings.%s" % self.value.setting_name, {"from django.conf import settings"}


class TupleSerializer(BaseSequenceSerializer):
    def _format(self):
        """
        Formats the given value into a string representation.
        
        Args:
        self: The instance of the class containing the 'value' attribute.
        
        Returns:
        A string representation of the 'value' attribute, formatted as a
        Python tuple. If the length of 'value' is 1, the returned string will
        include a trailing comma. If the length is 0, the returned string will
        be an empty tuple "()".
        
        Notes:
        - The function checks the length
        """

        # When len(value)==0, the empty tuple should be serialized as "()",
        # not "(,)" because (,) is invalid Python syntax.
        return "(%s)" if len(self.value) != 1 else "(%s,)"


class TypeSerializer(BaseSerializer):
    def serialize(self):
        """
        Serialize an object into a string representation.
        
        Args:
        self (Any): The object to be serialized.
        
        Returns:
        tuple: A tuple containing the string representation of the object and a set of import statements required for deserialization.
        
        Summary:
        This function takes an object and returns its string representation along with the necessary import statements. It handles special cases for `models.Model` and `None`. For other objects, it checks if the object has a `__module__` attribute and
        """

        special_cases = [
            (models.Model, "models.Model", []),
            (type(None), 'type(None)', []),
        ]
        for case, string, imports in special_cases:
            if case is self.value:
                return string, set(imports)
        if hasattr(self.value, "__module__"):
            module = self.value.__module__
            if module == builtins.__name__:
                return self.value.__name__, set()
            else:
                return "%s.%s" % (module, self.value.__name__), {"import %s" % module}


class UUIDSerializer(BaseSerializer):
    def serialize(self):
        return "uuid.%s" % repr(self.value), {"import uuid"}


class Serializer:
    _registry = {
        # Some of these are order-dependent.
        frozenset: FrozensetSerializer,
        list: SequenceSerializer,
        set: SetSerializer,
        tuple: TupleSerializer,
        dict: DictionarySerializer,
        models.Choices: ChoicesSerializer,
        enum.Enum: EnumSerializer,
        datetime.datetime: DatetimeDatetimeSerializer,
        (datetime.date, datetime.timedelta, datetime.time): DateTimeSerializer,
        SettingsReference: SettingsReferenceSerializer,
        float: FloatSerializer,
        (bool, int, type(None), bytes, str, range): BaseSimpleSerializer,
        decimal.Decimal: DecimalSerializer,
        (functools.partial, functools.partialmethod): FunctoolsPartialSerializer,
        (types.FunctionType, types.BuiltinFunctionType, types.MethodType): FunctionTypeSerializer,
        collections.abc.Iterable: IterableSerializer,
        (COMPILED_REGEX_TYPE, RegexObject): RegexSerializer,
        uuid.UUID: UUIDSerializer,
    }

    @classmethod
    def register(cls, type_, serializer):
        """
        Registers a serializer for a given type.
        
        Args:
        cls (type): The class to register the serializer with.
        type_ (type): The type to associate with the serializer.
        serializer (BaseSerializer): The serializer instance to register.
        
        Raises:
        ValueError: If the provided serializer does not inherit from `BaseSerializer`.
        
        Summary:
        This function registers a serializer for a specific type within a given class. It ensures that the provided serializer is an instance of `BaseSerializer`
        """

        if not issubclass(serializer, BaseSerializer):
            raise ValueError("'%s' must inherit from 'BaseSerializer'." % serializer.__name__)
        cls._registry[type_] = serializer

    @classmethod
    def unregister(cls, type_):
        cls._registry.pop(type_)


def serializer_factory(value):
    """
    Factory function to create a serializer based on the input value.
    
    Args:
    value: The value to be serialized.
    
    Returns:
    A serializer object based on the input value's type.
    
    Raises:
    ValueError: If the input value cannot be serialized.
    """

    if isinstance(value, Promise):
        value = str(value)
    elif isinstance(value, LazyObject):
        # The unwrapped value is returned as the first item of the arguments
        # tuple.
        value = value.__reduce__()[1][0]

    if isinstance(value, models.Field):
        return ModelFieldSerializer(value)
    if isinstance(value, models.manager.BaseManager):
        return ModelManagerSerializer(value)
    if isinstance(value, Operation):
        return OperationSerializer(value)
    if isinstance(value, type):
        return TypeSerializer(value)
    # Anything that knows how to deconstruct itself.
    if hasattr(value, 'deconstruct'):
        return DeconstructableSerializer(value)
    for type_, serializer_cls in Serializer._registry.items():
        if isinstance(value, type_):
            return serializer_cls(value)
    raise ValueError(
        "Cannot serialize: %r\nThere are some values Django cannot serialize into "
        "migration files.\nFor more, see https://docs.djangoproject.com/en/%s/"
        "topics/migrations/#migration-serializing" % (value, get_docs_version())
    )
