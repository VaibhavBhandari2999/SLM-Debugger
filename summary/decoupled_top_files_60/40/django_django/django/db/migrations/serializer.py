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
        Serializes a Django model path into a name and a set of import statements.
        
        This function takes a string `path` representing a Django model path and returns a tuple containing the serialized name and a set of import statements. The path is split into a module and a name. If the module is 'django.db.models', specific import statements for the models module are generated. Otherwise, a general import statement for the module is generated.
        
        Parameters:
        path (str): The Django model path to serialize.
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
        Serializes a dictionary into a string representation.
        
        This function takes a dictionary and recursively serializes its key-value pairs into a string format. The keys and values are serialized using appropriate serializers based on their types. The function returns a tuple containing the serialized string and a set of imported modules required for deserialization.
        
        Parameters:
        self (Serializer): The serializer instance to use for serialization.
        
        Returns:
        tuple: A tuple containing the serialized string and a set of imported modules.
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
        enum_class = self.value.__class__
        module = enum_class.__module__
        return (
            '%s.%s[%r]' % (module, enum_class.__qualname__, self.value.name),
            {'import %s' % module},
        )


class FloatSerializer(BaseSimpleSerializer):
    def serialize(self):
        """
        Serializes the value of the node into a Python expression.
        
        This method checks if the value is a NaN (Not a Number) or infinity. If so, it returns a string representation of the value wrapped in a Python float() function. Otherwise, it calls the superclass's serialize method to handle the serialization.
        
        Parameters:
        - self: The current instance of the class.
        
        Returns:
        - A tuple containing:
        - A string representing the serialized value.
        - A set of any additional information or flags
        """

        if math.isnan(self.value) or math.isinf(self.value):
            return 'float("{}")'.format(self.value), set()
        return super().serialize()


class FrozensetSerializer(BaseSequenceSerializer):
    def _format(self):
        return "frozenset([%s])"


class FunctionTypeSerializer(BaseSerializer):
    def serialize(self):
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
        Serialize a functools.partial object.
        
        This function takes a `functools.partial` object and serializes it into a string representation.
        The serialized string includes the function being partially applied, its arguments, and keyword arguments.
        
        Parameters:
        value (functools.partial): The `functools.partial` object to serialize.
        
        Returns:
        tuple: A tuple containing the serialized string and a set of import statements needed for deserialization.
        
        Example:
        >>> from functools import partial
        >>> def add(x
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
        Serializes a Django model manager or queryset.
        
        This function takes a deconstructed representation of a Django model manager or queryset and serializes it into a Python code string. The deconstructed representation includes the manager name, import paths, arguments, and keyword arguments.
        
        Parameters:
        - value (tuple): A deconstructed tuple representing the manager or queryset. The tuple contains the following elements:
        - as_manager (bool): Indicates if the object is a manager.
        - manager_path (str): The import
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
        Serializes a Django migration operation into a string representation.
        
        This function takes a Django migration operation and converts it into a string
        representation suitable for inclusion in a migration file. The operation is
        written with the specified indentation level (default is 0).
        
        Parameters:
        - self (Operation): The Django migration operation to serialize.
        
        Returns:
        - A tuple containing the serialized string and the required imports as a string.
        
        Note:
        - The trailing comma in the serialized string is removed.
        - The indentation level is set
        """

        from django.db.migrations.writer import OperationWriter
        string, imports = OperationWriter(self.value, indentation=0).serialize()
        # Nested operation, trailing comma is handled in upper OperationWriter._write()
        return string.rstrip(','), imports


class RegexSerializer(BaseSerializer):
    def serialize(self):
        """
        Serializes a regular expression pattern and its flags into a Python code string.
        
        This function takes a compiled regular expression object and converts its pattern and flags into a Python code string that can be used to recreate the regular expression. It also handles the serialization of any necessary imports.
        
        Parameters:
        self (RegexObject): The compiled regular expression object to serialize.
        
        Returns:
        tuple: A tuple containing the serialized Python code string and a set of import statements required to execute the code.
        
        Key Steps:
        1.
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
        Format a set literal in Python.
        
        This method returns a string representation of a set literal. If the set is not empty, it returns a formatted set literal enclosed in curly braces. If the set is empty, it returns 'set()' instead of '{}', to clearly indicate an empty set.
        
        Parameters:
        self (object): The object containing the set value to be formatted.
        
        Returns:
        str: A string representation of the set, formatted as a Python set literal.
        
        Example:
        >>> obj =
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
        Format a tuple for serialization.
        
        This method formats a tuple for serialization. If the tuple is empty, it returns an empty tuple "()". If the tuple contains a single element, it returns the element enclosed in parentheses and a comma "(,)" is omitted to avoid invalid Python syntax. For tuples with more than one element, it returns the elements enclosed in parentheses and separated by commas.
        
        Parameters:
        self (object): The object containing the tuple to be formatted.
        
        Returns:
        str: A string representation
        """

        # When len(value)==0, the empty tuple should be serialized as "()",
        # not "(,)" because (,) is invalid Python syntax.
        return "(%s)" if len(self.value) != 1 else "(%s,)"


class TypeSerializer(BaseSerializer):
    def serialize(self):
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
                return "%s.%s" % (module, self.value.__qualname__), {"import %s" % module}


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
        if not issubclass(serializer, BaseSerializer):
            raise ValueError("'%s' must inherit from 'BaseSerializer'." % serializer.__name__)
        cls._registry[type_] = serializer

    @classmethod
    def unregister(cls, type_):
        cls._registry.pop(type_)


def serializer_factory(value):
    """
    Generates a serializer for a given value based on its type.
    
    This function takes a value and determines the appropriate serializer to use
    based on the type of the value. If the value is an instance of `Promise` or
    `LazyObject`, it is converted to a string or unwrapped, respectively. It then
    checks if the value is an instance of `models.Field`, `models.manager.BaseManager`,
    or `Operation`, and returns the corresponding serializer. If the value is a
    class
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
