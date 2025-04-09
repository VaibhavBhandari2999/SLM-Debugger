import json

from django.contrib.postgres import lookups
from django.contrib.postgres.forms import SimpleArrayField
from django.contrib.postgres.validators import ArrayMaxLengthValidator
from django.core import checks, exceptions
from django.db.models import Field, IntegerField, Transform
from django.db.models.lookups import Exact, In
from django.utils.translation import gettext_lazy as _

from ..utils import prefix_validation_error
from .mixins import CheckFieldDefaultMixin
from .utils import AttributeSetter

__all__ = ['ArrayField']


class ArrayField(CheckFieldDefaultMixin, Field):
    empty_strings_allowed = False
    default_error_messages = {
        'item_invalid': _('Item %(nth)s in the array did not validate:'),
        'nested_array_mismatch': _('Nested arrays must have the same length.'),
    }
    _default_hint = ('list', '[]')

    def __init__(self, base_field, size=None, **kwargs):
        """
        Initializes an instance of the class with a base field and optional size parameter. Adds an ArrayMaxLengthValidator to the default validators if size is specified. If the base field has a from_db_value method, it sets the from_db_value method of the current instance to a custom implementation.
        
        Args:
        base_field (Field): The base field to use for this array field.
        size (int, optional): The maximum length of the array. Defaults to None.
        
        Returns:
        None
        """

        self.base_field = base_field
        self.size = size
        if self.size:
            self.default_validators = [*self.default_validators, ArrayMaxLengthValidator(self.size)]
        # For performance, only add a from_db_value() method if the base field
        # implements it.
        if hasattr(self.base_field, 'from_db_value'):
            self.from_db_value = self._from_db_value
        super().__init__(**kwargs)

    @property
    def model(self):
        """
        Retrieve the model attribute.
        
        This method attempts to access the 'model' attribute of the current
        instance. If the 'model' attribute is not found in the instance's
        dictionary, an `AttributeError` is raised with a descriptive message.
        
        Returns:
        The value of the 'model' attribute.
        
        Raises:
        AttributeError: If the 'model' attribute is not found in the instance's attributes.
        """

        try:
            return self.__dict__['model']
        except KeyError:
            raise AttributeError("'%s' object has no attribute 'model'" % self.__class__.__name__)

    @model.setter
    def model(self, model):
        self.__dict__['model'] = model
        self.base_field.model = model

    def check(self, **kwargs):
        """
        Checks the configuration of an array field.
        
        Args:
        **kwargs: Additional keyword arguments passed to the parent class's `check` method.
        
        Returns:
        A list of :class:`~django.core.checks.Error` objects indicating any issues found during validation.
        
        Raises:
        None
        
        Notes:
        - Validates that the base field is not a related field.
        - Inherits and processes errors from the base field's `check` method.
        """

        errors = super().check(**kwargs)
        if self.base_field.remote_field:
            errors.append(
                checks.Error(
                    'Base field for array cannot be a related field.',
                    obj=self,
                    id='postgres.E002'
                )
            )
        else:
            # Remove the field name checks as they are not needed here.
            base_errors = self.base_field.check()
            if base_errors:
                messages = '\n    '.join('%s (%s)' % (error.msg, error.id) for error in base_errors)
                errors.append(
                    checks.Error(
                        'Base field for array has errors:\n    %s' % messages,
                        obj=self,
                        id='postgres.E001'
                    )
                )
        return errors

    def set_attributes_from_name(self, name):
        super().set_attributes_from_name(name)
        self.base_field.set_attributes_from_name(name)

    @property
    def description(self):
        return 'Array of %s' % self.base_field.description

    def db_type(self, connection):
        size = self.size or ''
        return '%s[%s]' % (self.base_field.db_type(connection), size)

    def get_placeholder(self, value, compiler, connection):
        return '%s::{}'.format(self.db_type(connection))

    def get_db_prep_value(self, value, connection, prepared=False):
        """
        Converts a given value to a database-prepared value.
        
        This method handles lists or tuples by converting each element using
        the base field's `get_db_prep_value` method. For other types of values,
        it returns the value as is.
        
        Args:
        value: The value to be converted to a database-prepared value.
        connection: The database connection object.
        prepared: A boolean indicating whether the value has already been prepared.
        
        Returns:
        The database-prepared
        """

        if isinstance(value, (list, tuple)):
            return [self.base_field.get_db_prep_value(i, connection, prepared=False) for i in value]
        return value

    def deconstruct(self):
        """
        Deconstructs the ArrayField into its constituent parts.
        
        Args:
        None (This method is called internally by Django and does not accept any arguments).
        
        Returns:
        A tuple containing the following elements:
        - `name`: The name of the field.
        - `path`: The fully qualified path to the ArrayField class.
        - `args`: A list of positional arguments.
        - `kwargs`: A dictionary of keyword arguments, including the base field and size of the array field
        """

        name, path, args, kwargs = super().deconstruct()
        if path == 'django.contrib.postgres.fields.array.ArrayField':
            path = 'django.contrib.postgres.fields.ArrayField'
        kwargs.update({
            'base_field': self.base_field.clone(),
            'size': self.size,
        })
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
        
        This method first attempts to retrieve the transformation using the base class's `get_transform` method. If no transformation is found, it checks if the name contains an underscore ('_'). If so, it splits the name into start and end indices, converts them to integers, and returns a `SliceTransformFactory` with
        """

        transform = super().get_transform(name)
        if transform:
            return transform
        if '_' not in name:
            try:
                index = int(name)
            except ValueError:
                pass
            else:
                index += 1  # postgres uses 1-indexing
                return IndexTransformFactory(index, self.base_field)
        try:
            start, end = name.split('_')
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
                    prefix=self.error_messages['item_invalid'],
                    code='item_invalid',
                    params={'nth': index + 1},
                )
        if isinstance(self.base_field, ArrayField):
            if len({len(i) for i in value}) > 1:
                raise exceptions.ValidationError(
                    self.error_messages['nested_array_mismatch'],
                    code='nested_array_mismatch',
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
                    prefix=self.error_messages['item_invalid'],
                    code='item_invalid',
                    params={'nth': index + 1},
                )

    def formfield(self, **kwargs):
        """
        Generates a form field for the SimpleArrayField.
        
        This method creates a form field for the SimpleArrayField by utilizing the superclass's formfield method. It sets the form class to SimpleArrayField, the base field to the base_field's formfield, and the max length to the size of the current field. Additional keyword arguments can be passed through.
        
        Args:
        **kwargs: Additional keyword arguments to pass through.
        
        Returns:
        A form field instance configured for the SimpleArray
        """

        return super().formfield(**{
            'form_class': SimpleArrayField,
            'base_field': self.base_field.formfield(),
            'max_length': self.size,
            **kwargs,
        })


@ArrayField.register_lookup
class ArrayContains(lookups.DataContains):
    def as_sql(self, qn, connection):
        """
        Generates an SQL query for a database operation.
        
        Args:
        qn (function): A quoting function for the database backend.
        connection (object): A database connection object.
        
        Returns:
        tuple: A tuple containing the generated SQL query and parameters.
        
        This method extends the functionality of its superclass by appending the data type of the left-hand side field to the generated SQL query. The `as_sql` method from the superclass is called first to get the initial SQL query and parameters,
        """

        sql, params = super().as_sql(qn, connection)
        sql = '%s::%s' % (sql, self.lhs.output_field.db_type(connection))
        return sql, params


@ArrayField.register_lookup
class ArrayContainedBy(lookups.ContainedBy):
    def as_sql(self, qn, connection):
        """
        Generates an SQL query for a database operation.
        
        Args:
        qn (function): A quoting function for the database backend.
        connection (object): A database connection object.
        
        Returns:
        tuple: A tuple containing the generated SQL query and parameters.
        
        This method extends the functionality of its superclass by appending the data type of the left-hand side field to the generated SQL query. The `as_sql` method from the superclass is called first to get the initial SQL query and parameters,
        """

        sql, params = super().as_sql(qn, connection)
        sql = '%s::%s' % (sql, self.lhs.output_field.db_type(connection))
        return sql, params


@ArrayField.register_lookup
class ArrayExact(Exact):
    def as_sql(self, qn, connection):
        """
        Generates an SQL query for a database operation.
        
        Args:
        qn (function): A quoting function for the database backend.
        connection (object): A database connection object.
        
        Returns:
        tuple: A tuple containing the generated SQL query and parameters.
        
        This method extends the functionality of its superclass by appending the data type of the left-hand side field to the generated SQL query. The `as_sql` method from the superclass is called first to get the initial SQL query and parameters,
        """

        sql, params = super().as_sql(qn, connection)
        sql = '%s::%s' % (sql, self.lhs.output_field.db_type(connection))
        return sql, params


@ArrayField.register_lookup
class ArrayOverlap(lookups.Overlap):
    def as_sql(self, qn, connection):
        """
        Generates an SQL query for a database operation.
        
        Args:
        qn (function): A quoting function for the database backend.
        connection (object): A database connection object.
        
        Returns:
        tuple: A tuple containing the generated SQL query and parameters.
        
        This method extends the functionality of its superclass by appending the data type of the left-hand side field to the generated SQL query. The `as_sql` method from the superclass is called first to get the initial SQL query and parameters,
        """

        sql, params = super().as_sql(qn, connection)
        sql = '%s::%s' % (sql, self.lhs.output_field.db_type(connection))
        return sql, params


@ArrayField.register_lookup
class ArrayLenTransform(Transform):
    lookup_name = 'len'
    output_field = IntegerField()

    def as_sql(self, compiler, connection):
        """
        Generates SQL for checking if an array is null or has elements.
        
        Args:
        compiler: The SQL compiler object used to compile the left-hand side (lhs) expression.
        connection: The database connection object.
        
        Returns:
        A tuple containing:
        - A string representing the SQL query with placeholders for parameters.
        - A list of parameters to be used in the SQL query.
        
        Important Functions:
        - `compiler.compile`: Compiles the left-hand side (lhs) expression.
        """

        lhs, params = compiler.compile(self.lhs)
        # Distinguish NULL and empty arrays
        return (
            'CASE WHEN %(lhs)s IS NULL THEN NULL ELSE '
            'coalesce(array_length(%(lhs)s, 1), 0) END'
        ) % {'lhs': lhs}, params


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
        if hasattr(values, 'resolve_expression'):
            return values
        # In.process_rhs() expects values to be hashable, so convert lists
        # to tuples.
        prepared_values = []
        for value in values:
            if hasattr(value, 'resolve_expression'):
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
        lhs, params = compiler.compile(self.lhs)
        return '%s[%s]' % (lhs, self.index), params

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
        lhs, params = compiler.compile(self.lhs)
        return '%s[%s:%s]' % (lhs, self.start, self.end), params


class SliceTransformFactory:

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __call__(self, *args, **kwargs):
        return SliceTransform(self.start, self.end, *args, **kwargs)
