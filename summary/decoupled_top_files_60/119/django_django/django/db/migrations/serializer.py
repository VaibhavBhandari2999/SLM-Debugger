import builtins
import collections.abc
import datetime
import decimal
import enum
import functools
import math
import os
import pathlib
import re
import types
import uuid

from django.conf import SettingsReference
from django.db import models
from django.db.migrations.operations.base import Operation
from django.db.migrations.utils import COMPILED_REGEX_TYPE, RegexObject
from django.utils.functional import LazyObject, Promise
from django.utils.version import PY311, get_docs_version


class BaseSerializer:
    def __init__(self, value):
        self.value = value

    def serialize(self):
        raise NotImplementedError(
            "Subclasses of BaseSerializer must implement the serialize() method."
        )


class BaseSequenceSerializer(BaseSerializer):
    def _format(self):
        """
        Format the sequence data.
        
        This method is intended to be overridden by subclasses to provide specific formatting logic for the sequence data. It should not be called directly.
        
        Parameters:
        None
        
        Returns:
        str: The formatted sequence data.
        
        Raises:
        NotImplementedError: This method must be implemented by subclasses.
        """

        raise NotImplementedError(
            "Subclasses of BaseSequenceSerializer must implement the _format() method."
        )

    def serialize(self):
        """
        Serialize the value of the current object.
        
        This method serializes the value of the current object into a string representation, along with any necessary imports. The serialization process involves iterating over each item in the value, serializing each item using the appropriate serializer, and collecting the resulting strings and imports. The final string is formatted using the `_format` method.
        
        Parameters:
        None (the method operates on the current object's state)
        
        Returns:
        A tuple containing:
        - A string representing the serialized value
        """

        imports = set()
        strings = []
        for item in self.value:
            item_string, item_imports = serializer_factory(item).serialize()
            imports.update(item_imports)
            strings.append(item_string)
        value = self._format()
        return value % (", ".join(strings)), imports


class BaseUnorderedSequenceSerializer(BaseSequenceSerializer):
    def __init__(self, value):
        super().__init__(sorted(value, key=repr))


class BaseSimpleSerializer(BaseSerializer):
    def serialize(self):
        return repr(self.value), set()


class ChoicesSerializer(BaseSerializer):
    def serialize(self):
        return serializer_factory(self.value.value).serialize()


class DateTimeSerializer(BaseSerializer):
    """For datetime.*, except datetime.datetime."""

    def serialize(self):
        return repr(self.value), {"import datetime"}


class DatetimeDatetimeSerializer(BaseSerializer):
    """For datetime.datetime."""

    def serialize(self):
        if self.value.tzinfo is not None and self.value.tzinfo != datetime.timezone.utc:
            self.value = self.value.astimezone(datetime.timezone.utc)
        imports = ["import datetime"]
        return repr(self.value), set(imports)


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
        Serializes the dictionary into a string representation.
        
        This function takes a dictionary and serializes it into a string format. It processes each key-value pair in the dictionary, serializing them using the appropriate serializer based on the type of the value. The serialized key and value are then combined into a string representation of the dictionary.
        
        Parameters:
        self (Serializer): The serializer instance to use for serialization.
        
        Returns:
        tuple: A tuple containing the serialized string representation of the dictionary and a set of imported modules
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
        if issubclass(enum_class, enum.Flag):
            if PY311:
                members = list(self.value)
            else:
                members, _ = enum._decompose(enum_class, self.value)
                members = reversed(members)
        else:
            members = (self.value,)
        return (
            " | ".join(
                [
                    f"{module}.{enum_class.__qualname__}[{item.name!r}]"
                    for item in members
                ]
            ),
            {"import %s" % module},
        )


class FloatSerializer(BaseSimpleSerializer):
    def serialize(self):
        if math.isnan(self.value) or math.isinf(self.value):
            return 'float("{}")'.format(self.value), set()
        return super().serialize()


class FrozensetSerializer(BaseUnorderedSequenceSerializer):
    def _format(self):
        return "frozenset([%s])"


class FunctionTypeSerializer(BaseSerializer):
    def serialize(self):
        """
        Serializes a function into a string representation.
        
        This function takes a callable object (function or method) and returns a string representation of it, along with any necessary import statements. It handles different cases based on the type of the callable object, such as methods of a class, lambdas, or functions without a module.
        
        Parameters:
        value (callable): The callable object to serialize.
        
        Returns:
        tuple: A tuple containing the string representation of the callable and a dictionary of import statements required to make
        """

        if getattr(self.value, "__self__", None) and isinstance(
            self.value.__self__, type
        ):
            klass = self.value.__self__
            module = klass.__module__
            return "%s.%s.%s" % (module, klass.__name__, self.value.__name__), {
                "import %s" % module
            }
        # Further error checking
        if self.value.__name__ == "<lambda>":
            raise ValueError("Cannot serialize function: lambda")
        if self.value.__module__ is None:
            raise ValueError("Cannot serialize function %r: No module" % self.value)

        module_name = self.value.__module__

        if "<" not in self.value.__qualname__:  # Qualname can include <locals>
            return "%s.%s" % (module_name, self.value.__qualname__), {
                "import %s" % self.value.__module__
            }

        raise ValueError(
            "Could not find function %s in %s.\n" % (self.value.__name__, module_name)
        )


class FunctoolsPartialSerializer(BaseSerializer):
    def serialize(self):
        # Serialize functools.partial() arguments
        func_string, func_imports = serializer_factory(self.value.func).serialize()
        args_string, args_imports = serializer_factory(self.value.args).serialize()
        keywords_string, keywords_imports = serializer_factory(
            self.value.keywords
        ).serialize()
        # Add any imports needed by arguments
        imports = {"import functools", *func_imports, *args_imports, *keywords_imports}
        return (
            "functools.%s(%s, *%s, **%s)"
            % (
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
        Serializes a list of items into a string representation of a Python tuple.
        
        This function takes a list of items and serializes each item using a serializer
        generated by `serializer_factory`. It collects all the imported modules required
        for deserialization and returns a string representation of the tuple containing
        the serialized items.
        
        Parameters:
        self (object): The object containing the list of items to be serialized.
        
        Returns:
        tuple: A tuple containing the serialized string and a set of imported modules.
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
        Serialize a Django model manager or queryset.
        
        This function takes a deconstructed representation of a Django model manager or queryset and returns a serialized form of it. If the manager is an as_manager instance, it returns a string representing the manager with the as_manager method called. Otherwise, it calls the `serialize_deconstructed` method to serialize the manager path, arguments, and keyword arguments.
        
        Parameters:
        self (object): The current instance, which contains the deconstructed representation of the manager or queryset.
        
        Returns
        """

        as_manager, manager_path, qs_path, args, kwargs = self.value.deconstruct()
        if as_manager:
            name, imports = self._serialize_path(qs_path)
            return "%s.as_manager()" % name, imports
        else:
            return self.serialize_deconstructed(manager_path, args, kwargs)


class OperationSerializer(BaseSerializer):
    def serialize(self):
        from django.db.migrations.writer import OperationWriter

        string, imports = OperationWriter(self.value, indentation=0).serialize()
        # Nested operation, trailing comma is handled in upper OperationWriter._write()
        return string.rstrip(","), imports


class PathLikeSerializer(BaseSerializer):
    def serialize(self):
        return repr(os.fspath(self.value)), {}


class PathSerializer(BaseSerializer):
    def serialize(self):
        # Convert concrete paths to pure paths to avoid issues with migrations
        # generated on one platform being used on a different platform.
        prefix = "Pure" if isinstance(self.value, pathlib.Path) else ""
        return "pathlib.%s%r" % (prefix, self.value), {"import pathlib"}


class RegexSerializer(BaseSerializer):
    def serialize(self):
        regex_pattern, pattern_imports = serializer_factory(
            self.value.pattern
        ).serialize()
        # Turn off default implicit flags (e.g. re.U) because regexes with the
        # same implicit and explicit flags aren't equal.
        flags = self.value.flags ^ re.compile("").flags
        regex_flags, flag_imports = serializer_factory(flags).serialize()
        imports = {"import re", *pattern_imports, *flag_imports}
        args = [regex_pattern]
        if flags:
            args.append(regex_flags)
        return "re.compile(%s)" % ", ".join(args), imports


class SequenceSerializer(BaseSequenceSerializer):
    def _format(self):
        return "[%s]"


class SetSerializer(BaseUnorderedSequenceSerializer):
    def _format(self):
        """
        Format a set literal for the given value.
        
        This method serializes the value as a set literal. If the value is not empty, it is formatted as a set literal enclosed in curly braces. If the value is empty, it is formatted as a call to the `set` constructor with no arguments.
        
        Parameters:
        self (object): The object containing the value to be formatted.
        
        Returns:
        str: A string representation of the set literal or the call to the set constructor.
        
        Example:
        """

        # Serialize as a set literal except when value is empty because {}
        # is an empty dict.
        return "{%s}" if self.value else "set(%s)"


class SettingsReferenceSerializer(BaseSerializer):
    def serialize(self):
        return "settings.%s" % self.value.setting_name, {
            "from django.conf import settings"
        }


class TupleSerializer(BaseSequenceSerializer):
    def _format(self):
        # When len(value)==0, the empty tuple should be serialized as "()",
        # not "(,)" because (,) is invalid Python syntax.
        return "(%s)" if len(self.value) != 1 else "(%s,)"


class TypeSerializer(BaseSerializer):
    def serialize(self):
        special_cases = [
            (models.Model, "models.Model", ["from django.db import models"]),
            (types.NoneType, "types.NoneType", ["import types"]),
        ]
        for case, string, imports in special_cases:
            if case is self.value:
                return string, set(imports)
        if hasattr(self.value, "__module__"):
            module = self.value.__module__
            if module == builtins.__name__:
                return self.value.__name__, set()
            else:
                return "%s.%s" % (module, self.value.__qualname__), {
                    "import %s" % module
                }


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
        (bool, int, types.NoneType, bytes, str, range): BaseSimpleSerializer,
        decimal.Decimal: DecimalSerializer,
        (functools.partial, functools.partialmethod): FunctoolsPartialSerializer,
        (
            types.FunctionType,
            types.BuiltinFunctionType,
            types.MethodType,
        ): FunctionTypeSerializer,
        collections.abc.Iterable: IterableSerializer,
        (COMPILED_REGEX_TYPE, RegexObject): RegexSerializer,
        uuid.UUID: UUIDSerializer,
        pathlib.PurePath: PathSerializer,
        os.PathLike: PathLikeSerializer,
    }

    @classmethod
    def register(cls, type_, serializer):
        if not issubclass(serializer, BaseSerializer):
            raise ValueError(
                "'%s' must inherit from 'BaseSerializer'." % serializer.__name__
            )
        cls._registry[type_] = serializer

    @classmethod
    def unregister(cls, type_):
        cls._registry.pop(type_)


def serializer_factory(value):
    """
    Generates a serializer for a given value based on its type.
    
    This function takes a value and determines the appropriate serializer based on the type of the value. If the value is a subclass of `Promise` or `LazyObject`, it is converted to a string or its unwrapped value, respectively. The function then checks if the value is an instance of `models.Field`, `models.manager.BaseManager`, `Operation`, or `type`, and returns a specific serializer for each case. If the value
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
    if hasattr(value, "deconstruct"):
        return DeconstructableSerializer(value)
    for type_, serializer_cls in Serializer._registry.items():
        if isinstance(value, type_):
            return serializer_cls(value)
    raise ValueError(
        "Cannot serialize: %r\nThere are some values Django cannot serialize into "
        "migration files.\nFor more, see https://docs.djangoproject.com/en/%s/"
        "topics/migrations/#migration-serializing" % (value, get_docs_version())
    )
    if isinstance(value, type):
        return TypeSerializer(value)
    # Anything that knows how to deconstruct itself.
    if hasattr(value, "deconstruct"):
        return DeconstructableSerializer(value)
    for type_, serializer_cls in Serializer._registry.items():
        if isinstance(value, type_):
            return serializer_cls(value)
    raise ValueError(
        "Cannot serialize: %r\nThere are some values Django cannot serialize into "
        "migration files.\nFor more, see https://docs.djangoproject.com/en/%s/"
        "topics/migrations/#migration-serializing" % (value, get_docs_version())
    )
e, get_docs_version())
    )
