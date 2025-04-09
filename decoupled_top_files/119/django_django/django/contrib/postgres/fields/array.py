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
        """
        Initializes an instance of the class with a base field, size (optional), and additional keyword arguments.
        
        Args:
        base_field: The base field to initialize the instance with.
        size: The maximum length of the array (optional).
        **kwargs: Additional keyword arguments to pass to the superclass.
        
        Summary:
        - Sets the `base_field` attribute.
        - Retrieves the `db_collation` attribute from the `base_field`.
        - Adds an `ArrayMaxLengthValidator`
        """

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
        """
        Retrieve the model attribute.
        
        This method attempts to access the 'model' attribute from the instance's
        dictionary. If the attribute does not exist, it raises an `AttributeError`
        with a descriptive message indicating the class name and the missing
        attribute.
        
        Returns:
        The value of the 'model' attribute.
        
        Raises:
        AttributeError: If the 'model' attribute is not found in the instance's
        dictionary.
        
        Notes:
        - The method uses the `
        """

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
        """
        Checks the configuration of an array field.
        
        Args:
        **kwargs: Additional keyword arguments passed to the parent class's `check` method.
        
        Returns:
        A list of :class:`~django.core.checks.Error` or :class:`~django.core.checks.Warning` objects indicating any issues found with the array field configuration.
        
        Raises:
        None
        
        Notes:
        - This method first calls the parent class's `check` method to perform initial validation.
        - It then checks if
        """

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
        """
        Retrieves database parameters from the superclass and sets the collation parameter.
        
        Args:
        connection: The database connection object.
        
        Returns:
        A dictionary containing the database parameters with the collation set to the instance's db_collation value.
        """

        db_params = super().db_parameters(connection)
        db_params["collation"] = self.db_collation
        return db_params

    def get_placeholder(self, value, compiler, connection):
        return "%s::{}".format(self.db_type(connection))

    def get_db_prep_value(self, value, connection, prepared=False):
        """
        Prepares a value for database storage.
        
        This method processes the given value, ensuring it is suitable for
        database storage. If the value is a list or tuple, it recursively
        processes each element using the base field's `get_db_prep_value`
        method. Otherwise, it returns the value as-is.
        
        Args:
        value: The value to be prepared for database storage.
        connection: The database connection object.
        prepared: A boolean indicating whether the value has already
        """

        if isinstance(value, (list, tuple)):
            return [
                self.base_field.get_db_prep_value(i, connection, prepared=False)
                for i in value
            ]
        return value

    def deconstruct(self):
        """
        Deconstructs the ArrayField into its components.
        
        Args:
        None (This method is called internally by Django and does not take any explicit arguments).
        
        Returns:
        A tuple containing the following elements:
        - `name`: The name of the field.
        - `path`: The fully qualified path to the ArrayField class.
        - `args`: A list of positional arguments.
        - `kwargs`: A dictionary of keyword arguments, including the base field and size.
        
        Notes:
        """

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
        """
        Converts a given value to a Python object.
        
        Args:
        value (str): The value to be converted.
        
        Returns:
        list: A list of values after conversion.
        
        Summary:
        This function takes a string `value` and converts it into a Python object. If the input is a string, it is assumed that the string contains a JSON representation of a list. The function uses `json.loads()` to parse the string into a Python list. Then, it iterates over
        """

        if isinstance(value, str):
            # Assume we're deserializing
            vals = json.loads(value)
            value = [self.base_field.to_python(val) for val in vals]
        return value

    def _from_db_value(self, value, expression, connection):
        """
        Extracts a list of values from a database field.
        
        This method processes a value retrieved from the database and converts it into a list of items. If the value is `None`, it returns `None`. Otherwise, it iterates over the value (which is expected to be an iterable) and applies the `from_db_value` method of the base field to each item, effectively converting each item according to its type.
        
        Args:
        value (Iterable): The value retrieved from the database.
        """

        if value is None:
            return value
        return [
            self.base_field.from_db_value(item, expression, connection)
            for item in value
        ]

    def value_to_string(self, obj):
        """
        Converts an object's attribute values to a JSON string.
        
        This function takes an object and extracts its attribute values using
        `value_from_object`. It then processes each value, converting them to a
        string representation using the `value_to_string` method of the `base_field`
        field. If a value is `None`, it is appended as is. Otherwise, an instance
        of `AttributeSetter` is created with the attribute name and value, and its
        `
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
        """
        Retrieve a transformation based on the given name.
        
        Args:
        name (str): The name of the transformation to retrieve.
        
        Returns:
        Transform: The requested transformation object.
        
        This method first attempts to retrieve the transformation using the base class's `get_transform` method. If no transformation is found, it checks if the name contains an integer, which is interpreted as an index for an `IndexTransformFactory`. If the name does not contain an integer but contains two integers separated by an underscore
        """

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
        """
        Validates a list of values against the base field. Raises ValidationError if any part is invalid.
        
        Args:
        value (list): The list of values to be validated.
        model_instance (object): The instance of the model being validated.
        
        Raises:
        ValidationError: If any part of the list fails validation or if the lengths of nested arrays are inconsistent.
        """

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
        """
        Runs validators on the given value. Iterates over each part of the value and runs the base field's validators on it. Raises a ValidationError with a custom message if any part fails validation.
        
        Args:
        value (list): The list of parts to validate.
        
        Raises:
        ValidationError: If any part of the value fails validation.
        """

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
        
        This method creates a form field for a custom array field by utilizing the `SimpleArrayField` class and the `base_field.formfield()` method. The `max_length` parameter is set to the size of the array field. Additional keyword arguments can be passed through the `**kwargs` parameter.
        
        Args:
        **kwargs: Additional keyword arguments to be passed to the form field.
        
        Returns:
        A form field instance for the
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
        """
        Initialize a new instance of the class.
        
        Args:
        lhs: The left-hand side expression or field.
        rhs: The right-hand side expression or array of values.
        
        Summary:
        This method initializes a new instance of the class by processing the `rhs` argument. If `rhs` is a tuple or list containing non-None values, it creates an array using the `ARRAY` function from the `Func` class. If `rhs` is a single value without a `resolve
        """

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
        """
        Processes the right-hand side of a query.
        
        Args:
        compiler: The database compiler instance.
        connection: The database connection object.
        
        Returns:
        A tuple containing the processed right-hand side and its parameters.
        """

        rhs, rhs_params = super().process_rhs(compiler, connection)
        cast_type = self.lhs.output_field.cast_db_type(connection)
        return "%s::%s" % (rhs, cast_type), rhs_params

    def _rhs_not_none_values(self, rhs):
        """
        Yields `True` for each non-None value in the given iterable `rhs`. Recursively processes nested lists and tuples.
        
        Args:
        rhs (Iterable): The input iterable containing values or nested iterables.
        
        Yields:
        bool: `True` for each non-None value found.
        """

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
        Generates SQL for checking if an array is null or has elements.
        
        Args:
        compiler: The SQL compiler instance used to compile the left-hand side expression.
        connection: The database connection object.
        
        Returns:
        A tuple containing the generated SQL query and parameters.
        
        Summary:
        This function compiles the left-hand side expression using the provided compiler and then constructs a SQL query to check if the resulting array is null or has elements. It uses `array_length` and `coalesce
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
        """
        Prepares a lookup value for database query.
        
        This method processes the lookup value to ensure it is suitable for use
        in a database query. It first calls the superclass's `get_prep_lookup`
        method to obtain the initial prepared values. If these values are
        expressions (i.e., they have a `resolve_expression` attribute), they are
        returned as-is. Otherwise, the method converts any non-expression values
        to tuples to make them hashable, as required
        """

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
        """
        Initialize a new instance of the class.
        
        Args:
        index (int): The index of the field.
        base_field (str): The base field of the field.
        
        Returns:
        None
        
        This method initializes a new instance of the class with the given index and base field. It also calls the superclass's `__init__` method with the provided arguments.
        """

        super().__init__(*args, **kwargs)
        self.index = index
        self.base_field = base_field

    def as_sql(self, compiler, connection):
        """
        Generates an SQL query for accessing elements of a list or array.
        
        Args:
        compiler: The SQL compiler object responsible for compiling the left-hand side (lhs) expression.
        connection: The database connection object.
        
        Returns:
        A tuple containing the generated SQL query and a list of parameters.
        
        Summary:
        This function takes a left-hand side expression, compiles it using the provided compiler, and generates an SQL query to access an element from a list or array. If the compiled
        """

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
        """
        Initialize a new instance of the class.
        
        Args:
        start (int): The starting value of the range.
        end (int): The ending value of the range.
        
        Attributes:
        start (int): The starting value of the range.
        end (int): The ending value of the range.
        """

        super().__init__(*args, **kwargs)
        self.start = start
        self.end = end

    def as_sql(self, compiler, connection):
        """
        Generates an SQL query for accessing elements within a list or array.
        
        Args:
        compiler (Compiler): The compiler object responsible for compiling the query.
        connection (Connection): The database connection object.
        
        Returns:
        str: The generated SQL query.
        tuple: Parameters to be used in the SQL query.
        
        Summary:
        This function takes a compiler and a connection object as inputs and generates an SQL query for accessing elements within a list or array. It compiles the left-hand side
        """

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
