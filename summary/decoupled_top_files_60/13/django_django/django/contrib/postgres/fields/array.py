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
        Retrieve the model attribute of the object.
        
        This method attempts to return the 'model' attribute of the object. If the 'model' attribute is not found in the object's dictionary, it raises an AttributeError with a descriptive message.
        
        Parameters:
        None
        
        Returns:
        dict: The 'model' attribute of the object if it exists.
        
        Raises:
        AttributeError: If the 'model' attribute is not found in the object's dictionary.
        
        Example:
        >>> obj = SomeClass()
        >>> obj
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
        if isinstance(value, (list, tuple)):
            return [self.base_field.get_db_prep_value(i, connection, prepared=False) for i in value]
        return value

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if path == 'django.contrib.postgres.fields.array.ArrayField':
            path = 'django.contrib.postgres.fields.ArrayField'
        kwargs.update({
            'base_field': self.base_field.clone(),
            'size': self.size,
        })
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
        Retrieve a transformation object by name.
        
        Args:
        name (str): The name of the transformation to retrieve.
        
        Returns:
        Transform: The transformation object if found, otherwise None.
        
        This function first attempts to retrieve the transformation using the provided name. If the transformation is not found, it checks if the name is a valid index (considering 1-based indexing for consistency with PostgreSQL). If the name is a valid index, it returns an `IndexTransformFactory` instance with the adjusted index. If
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
        Validate a list of values against a base field.
        
        This method validates a list of values against the base field, raising specific validation errors if any part of the list fails validation. It also checks for nested array mismatches if the base field is an instance of ArrayField.
        
        Parameters:
        value (list): The list of values to validate.
        model_instance (object): The model instance associated with the validation.
        
        Returns:
        None: This method does not return a value. It raises ValidationError if validation
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
        return super().formfield(**{
            'form_class': SimpleArrayField,
            'base_field': self.base_field.formfield(),
            'max_length': self.size,
            **kwargs,
        })


@ArrayField.register_lookup
class ArrayContains(lookups.DataContains):
    def as_sql(self, qn, connection):
        sql, params = super().as_sql(qn, connection)
        sql = '%s::%s' % (sql, self.lhs.output_field.db_type(connection))
        return sql, params


@ArrayField.register_lookup
class ArrayContainedBy(lookups.ContainedBy):
    def as_sql(self, qn, connection):
        """
        Generate a SQL query for a database operation.
        
        This function is responsible for converting a Django ORM query into a SQL query string suitable for execution on a database. It extends the functionality of a superclass method to include the data type of the left-hand side (lhs) field in the generated SQL.
        
        Parameters:
        qn (function): A quoting function that is used to safely quote identifiers in the SQL query.
        connection (object): A database connection object that provides information about the current database backend, including
        """

        sql, params = super().as_sql(qn, connection)
        sql = '%s::%s' % (sql, self.lhs.output_field.db_type(connection))
        return sql, params


@ArrayField.register_lookup
class ArrayExact(Exact):
    def as_sql(self, qn, connection):
        sql, params = super().as_sql(qn, connection)
        sql = '%s::%s' % (sql, self.lhs.output_field.db_type(connection))
        return sql, params


@ArrayField.register_lookup
class ArrayOverlap(lookups.Overlap):
    def as_sql(self, qn, connection):
        sql, params = super().as_sql(qn, connection)
        sql = '%s::%s' % (sql, self.lhs.output_field.db_type(connection))
        return sql, params


@ArrayField.register_lookup
class ArrayLenTransform(Transform):
    lookup_name = 'len'
    output_field = IntegerField()

    def as_sql(self, compiler, connection):
        lhs, params = compiler.compile(self.lhs)
        # Distinguish NULL and empty arrays
        return (
            'CASE WHEN %(lhs)s IS NULL THEN NULL ELSE '
            'coalesce(array_length(%(lhs)s, 1), 0) END'
        ) % {'lhs': lhs}, params


@ArrayField.register_lookup
class ArrayInLookup(In):
    def get_prep_lookup(self):
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
self.base_field, *args, **kwargs)


class SliceTransform(Transform):

    def __init__(self, start, end, *args, **kwargs):
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
