import json

from django.contrib.postgres import lookups
from django.contrib.postgres.forms import SimpleArrayField
from django.contrib.postgres.validators import ArrayMaxLengthValidator
from django.core import checks, exceptions
from django.db.models import Field, Func, IntegerField, Transform, Value
from django.db.models.fields.mixins import CheckFieldDefaultMixin
from django.db.models.lookups import Exact, In
from django.utils.translation import gettext_lazy as _

from ..utils import prefix_validation_error
from .utils import AttributeSetter

__all__ = ["ArrayField"]


class ArrayField(CheckFieldDefaultMixin, Field):
    empty_strings_allowed = False
    default_error_messages = {
        "item_invalid": _("Item %(nth)s in the array did not validate:"),
        "nested_array_mismatch": _("Nested arrays must have the same length."),
    }
    _default_hint = ("list", "[]")

    def __init__(self, base_field, size=None, **kwargs):
        self.base_field = base_field
        self.db_collation = getattr(self.base_field, "db_collation", None)
        self.size = size
        if self.size:
            self.default_validators = [
                *self.default_validators,
                ArrayMaxLengthValidator(self.size),
            ]
        # For performance, only add a from_db_value() method if the base field
        # implements it.
        if hasattr(self.base_field, "from_db_value"):
            self.from_db_value = self._from_db_value
        super().__init__(**kwargs)

    @property
    def model(self):
        try:
            return self.__dict__["model"]
        except KeyError:
            raise AttributeError(
                "'%s' object has no attribute 'model'" % self.__class__.__name__
            )

    @model.setter
    def model(self, model):
        self.__dict__["model"] = model
        self.base_field.model = model

    @classmethod
    def _choices_is_value(cls, value):
        return isinstance(value, (list, tuple)) or super()._choices_is_value(value)

    def check(self, **kwargs):
        errors = super().check(**kwargs)
        if self.base_field.remote_field:
            errors.append(
                checks.Error(
                    "Base field for array cannot be a related field.",
                    obj=self,
                    id="postgres.E002",
                )
            )
        else:
            # Remove the field name checks as they are not needed here.
            base_checks = self.base_field.check()
            if base_checks:
                error_messages = "\n    ".join(
                    "%s (%s)" % (base_check.msg, base_check.id)
                    for base_check in base_checks
                    if isinstance(base_check, checks.Error)
                )
                if error_messages:
                    errors.append(
                        checks.Error(
                            "Base field for array has errors:\n    %s" % error_messages,
                            obj=self,
                            id="postgres.E001",
                        )
                    )
                warning_messages = "\n    ".join(
                    "%s (%s)" % (base_check.msg, base_check.id)
                    for base_check in base_checks
                    if isinstance(base_check, checks.Warning)
                )
                if warning_messages:
                    errors.append(
                        checks.Warning(
                            "Base field for array has warnings:\n    %s"
                            % warning_messages,
                            obj=self,
                            id="postgres.W004",
                        )
                    )
        return errors

    def set_attributes_from_name(self, name):
        super().set_attributes_from_name(name)
        self.base_field.set_attributes_from_name(name)

    @property
    def description(self):
        return "Array of %s" % self.base_field.description

    def db_type(self, connection):
        size = self.size or ""
        return "%s[%s]" % (self.base_field.db_type(connection), size)

    def cast_db_type(self, connection):
        size = self.size or ""
        return "%s[%s]" % (self.base_field.cast_db_type(connection), size)

    def db_parameters(self, connection):
        db_params = super().db_parameters(connection)
        db_params["collation"] = self.db_collation
        return db_params

    def get_placeholder(self, value, compiler, connection):
        return "%s::{}".format(self.db_type(connection))

    def get_db_prep_value(self, value, connection, prepared=False):
        """
        Generates a database-prepared value for a given input.
        
        This method is used to prepare a value for storage in a database. If the input value is a list or tuple, it processes each element of the list or tuple using the base field's `get_db_prep_value` method. If the input is not a list or tuple, it returns the value as is.
        
        Parameters:
        value (any): The value to be prepared for database storage.
        connection (object): The database connection object
        """

        if isinstance(value, (list, tuple)):
            return [
                self.base_field.get_db_prep_value(i, connection, prepared=False)
                for i in value
            ]
        return value

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if path == "django.contrib.postgres.fields.array.ArrayField":
            path = "django.contrib.postgres.fields.ArrayField"
        kwargs.update(
            {
                "base_field": self.base_field.clone(),
                "size": self.size,
            }
        )
        return name, path, args, kwargs

    def to_python(self, value):
        if isinstance(value, str):
            # Assume we're deserializing
            vals = json.loads(value)
            value = [self.base_field.to_python(val) for val in vals]
        return value

    def _from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return [
            self.base_field.from_db_value(item, expression, connection)
            for item in value
        ]

    def value_to_string(self, obj):
        """
        Converts the given object's attributes to a string representation.
        
        This function takes an object and extracts its attribute values using the `value_from_object` method. It then processes each value, converting it to a string using the base field's `value_to_string` method. If a value is None, it is directly appended as None. Otherwise, an `AttributeSetter` object is created for each non-None value, and its string representation is obtained. Finally, the list of string representations is converted
        """

        values = []
        vals = self.value_from_object(obj)
        base_field = self.base_field

        for val in vals:
            if val is None:
                values.append(None)
            else:
                obj = AttributeSetter(base_field.attname, val)
                values.append(base_field.value_to_string(obj))
        return json.dumps(values)

    def get_transform(self, name):
        transform = super().get_transform(name)
        if transform:
            return transform
        if "_" not in name:
            try:
                index = int(name)
            except ValueError:
                pass
            else:
                index += 1  # postgres uses 1-indexing
                return IndexTransformFactory(index, self.base_field)
        try:
            start, end = name.split("_")
            start = int(start) + 1
            end = int(end)  # don't add one here because postgres slices are weird
        except ValueError:
            pass
        else:
            return SliceTransformFactory(start, end)

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        for index, part in enumerate(value):
            try:
                self.base_field.validate(part, model_instance)
            except exceptions.ValidationError as error:
                raise prefix_validation_error(
                    error,
                    prefix=self.error_messages["item_invalid"],
                    code="item_invalid",
                    params={"nth": index + 1},
                )
        if isinstance(self.base_field, ArrayField):
            if len({len(i) for i in value}) > 1:
                raise exceptions.ValidationError(
                    self.error_messages["nested_array_mismatch"],
                    code="nested_array_mismatch",
                )

    def run_validators(self, value):
        super().run_validators(value)
        for index, part in enumerate(value):
            try:
                self.base_field.run_validators(part)
            except exceptions.ValidationError as error:
                raise prefix_validation_error(
                    error,
                    prefix=self.error_messages["item_invalid"],
                    code="item_invalid",
                    params={"nth": index + 1},
                )

    def formfield(self, **kwargs):
        """
        Generates a form field for a custom array field.
        
        This method is responsible for creating a form field for a custom array field. It leverages the `SimpleArrayField` and `base_field.formfield()` to generate the field. The `max_length` is set to the size of the array field.
        
        Parameters:
        **kwargs: Additional keyword arguments to be passed to the form field.
        
        Returns:
        A form field instance configured for the custom array field.
        
        Key Parameters:
        - `form
        """

        return super().formfield(
            **{
                "form_class": SimpleArrayField,
                "base_field": self.base_field.formfield(),
                "max_length": self.size,
                **kwargs,
            }
        )


class ArrayRHSMixin:
    def __init__(self, lhs, rhs):
        # Don't wrap arrays that contains only None values, psycopg doesn't
        # allow this.
        if isinstance(rhs, (tuple, list)) and any(self._rhs_not_none_values(rhs)):
            expressions = []
            for value in rhs:
                if not hasattr(value, "resolve_expression"):
                    field = lhs.output_field
                    value = Value(field.base_field.get_prep_value(value))
                expressions.append(value)
            rhs = Func(
                *expressions,
                function="ARRAY",
                template="%(function)s[%(expressions)s]",
            )
        super().__init__(lhs, rhs)

    def process_rhs(self, compiler, connection):
        rhs, rhs_params = super().process_rhs(compiler, connection)
        cast_type = self.lhs.output_field.cast_db_type(connection)
        return "%s::%s" % (rhs, cast_type), rhs_params

    def _rhs_not_none_values(self, rhs):
        for x in rhs:
            if isinstance(x, (list, tuple)):
                yield from self._rhs_not_none_values(x)
            elif x is not None:
                yield True


@ArrayField.register_lookup
class ArrayContains(ArrayRHSMixin, lookups.DataContains):
    pass


@ArrayField.register_lookup
class ArrayContainedBy(ArrayRHSMixin, lookups.ContainedBy):
    pass


@ArrayField.register_lookup
class ArrayExact(ArrayRHSMixin, Exact):
    pass


@ArrayField.register_lookup
class ArrayOverlap(ArrayRHSMixin, lookups.Overlap):
    pass


@ArrayField.register_lookup
class ArrayLenTransform(Transform):
    lookup_name = "len"
    output_field = IntegerField()

    def as_sql(self, compiler, connection):
        """
        Generates a SQL query to check if an array is NULL or empty.
        
        This function is used to create a SQL query that checks if an array is either NULL or empty. It takes a compiler and a database connection as inputs and returns a SQL query string along with any necessary parameters.
        
        Parameters:
        compiler (object): The compiler object used to compile the left-hand side (lhs) of the query.
        connection (object): The database connection object.
        
        Returns:
        tuple: A tuple containing the
        """

        lhs, params = compiler.compile(self.lhs)
        # Distinguish NULL and empty arrays
        return (
            "CASE WHEN %(lhs)s IS NULL THEN NULL ELSE "
            "coalesce(array_length(%(lhs)s, 1), 0) END"
        ) % {"lhs": lhs}, params * 2


@ArrayField.register_lookup
class ArrayInLookup(In):
    def get_prep_lookup(self):
        values = super().get_prep_lookup()
        if hasattr(values, "resolve_expression"):
            return values
        # In.process_rhs() expects values to be hashable, so convert lists
        # to tuples.
        prepared_values = []
        for value in values:
            if hasattr(value, "resolve_expression"):
                prepared_values.append(value)
            else:
                prepared_values.append(tuple(value))
        return prepared_values


class IndexTransform(Transform):
    def __init__(self, index, base_field, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = index
        self.base_field = base_field

    def as_sql(self, compiler, connection):
        lhs, params = compiler.compile(self.lhs)
        if not lhs.endswith("]"):
            lhs = "(%s)" % lhs
        return "%s[%%s]" % lhs, (*params, self.index)

    @property
    def output_field(self):
        return self.base_field


class IndexTransformFactory:
    def __init__(self, index, base_field):
        self.index = index
        self.base_field = base_field

    def __call__(self, *args, **kwargs):
        return IndexTransform(self.index, self.base_field, *args, **kwargs)


class SliceTransform(Transform):
    def __init__(self, start, end, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start = start
        self.end = end

    def as_sql(self, compiler, connection):
        lhs, params = compiler.compile(self.lhs)
        if not lhs.endswith("]"):
            lhs = "(%s)" % lhs
        return "%s[%%s:%%s]" % lhs, (*params, self.start, self.end)


class SliceTransformFactory:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __call__(self, *args, **kwargs):
        return SliceTransform(self.start, self.end, *args, **kwargs)
def __call__(self, *args, **kwargs):
        return SliceTransform(self.start, self.end, *args, **kwargs)
