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
        Initialize a custom field with a base field and optional size.
        
        Args:
        base_field (Field): The base field to use for this custom field.
        size (int, optional): The maximum length of the array. If provided, an ArrayMaxLengthValidator will be added to the default validators.
        
        Keyword Args:
        **kwargs: Additional keyword arguments to pass to the superclass initializer.
        
        Returns:
        None: This function does not return any value. It initializes the custom field object.
        
        Example:
        >>>
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
        try:
            return self.__dict__['model']
        except KeyError:
            raise AttributeError("'%s' object has no attribute 'model'" % self.__class__.__name__)

    @model.setter
    def model(self, model):
        self.__dict__['model'] = model
        self.base_field.model = model

    @classmethod
    def _choices_is_value(cls, value):
        return isinstance(value, (list, tuple)) or super()._choices_is_value(value)

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

    def cast_db_type(self, connection):
        size = self.size or ''
        return '%s[%s]' % (self.base_field.cast_db_type(connection), size)

    def get_placeholder(self, value, compiler, connection):
        return '%s::{}'.format(self.db_type(connection))

    def get_db_prep_value(self, value, connection, prepared=False):
        if isinstance(value, (list, tuple)):
            return [self.base_field.get_db_prep_value(i, connection, prepared=False) for i in value]
        return value

    def deconstruct(self):
        """
        Deconstructs the ArrayField instance for serialization.
        
        This method is used to deconstruct the ArrayField instance into its component parts for serialization purposes. It extracts the name, path, arguments, and keyword arguments of the field. If the path is 'django.contrib.postgres.fields.array.ArrayField', it is updated to 'django.contrib.postgres.fields.ArrayField'. The method then updates the keyword arguments with the cloned base field and the size of the array field.
        
        Parameters:
        None (This method is
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
        if isinstance(value, str):
            # Assume we're deserializing
            vals = json.loads(value)
            value = [self.base_field.to_python(val) for val in vals]
        return value

    def _from_db_value(self, value, expression, connection):
        """
        Converts a database value to a Python list of values.
        
        This method is used to transform a database value, which is expected to be a serialized list, into a Python list of values. If the database value is `None`, it is returned as is. Otherwise, it iterates over the serialized list and converts each item using the `from_db_value` method of the associated base field.
        
        Parameters:
        value (Any): The database value to be converted.
        expression (Expression): The expression
        """

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
        Validate a list of values against the base field.
        
        This method validates each element in the provided list against the base field. If any element fails validation, a ValidationError is raised with a specific error message. Additionally, if the base field is an ArrayField and the lengths of the inner lists are not uniform, a ValidationError is raised indicating a mismatch.
        
        Parameters:
        value (list): The list of values to validate.
        model_instance (object): The model instance associated with the validation.
        
        Returns:
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


class ArrayRHSMixin:
    def __init__(self, lhs, rhs):
        if isinstance(rhs, (tuple, list)):
            expressions = []
            for value in rhs:
                if not hasattr(value, 'resolve_expression'):
                    field = lhs.output_field
                    value = Value(field.base_field.get_prep_value(value))
                expressions.append(value)
            rhs = Func(
                *expressions,
                function='ARRAY',
                template='%(function)s[%(expressions)s]',
            )
        super().__init__(lhs, rhs)

    def process_rhs(self, compiler, connection):
        """
        Process the right-hand side (rhs) of a database query for a specific field.
        
        This method is overridden to customize the processing of the right-hand side of a database query. It first calls the superclass's `process_rhs` method to handle the default processing. Then, it determines the cast type required for the field based on its output field's database type. Finally, it returns a formatted string that includes the cast type and the parameters processed by the superclass.
        
        Parameters:
        compiler (sql.compiler.SQL
        """

        rhs, rhs_params = super().process_rhs(compiler, connection)
        cast_type = self.lhs.output_field.cast_db_type(connection)
        return '%s::%s' % (rhs, cast_type), rhs_params


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
        """
        Generates a prepared lookup value for database queries.
        
        This method processes the lookup values to ensure they are suitable for database queries. It first calls the superclass's `get_prep_lookup` method to get the initial values. If the values are expressions (i.e., they have a `resolve_expression` attribute), they are returned as-is. Otherwise, the values are converted to tuples to make them hashable, which is a requirement for certain database operations. This function is useful for preparing lookup values in database
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
        base_field (str): The base field for the instance.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
        
        Returns:
        None: This function does not return any value.
        """

        super().__init__(*args, **kwargs)
        self.index = index
        self.base_field = base_field

    def as_sql(self, compiler, connection):
        lhs, params = compiler.compile(self.lhs)
        return '%s[%%s]' % lhs, params + [self.index]

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
        Initialize a Range object.
        
        Args:
        start (int): The starting value of the range.
        end (int): The ending value of the range.
        *args: Additional positional arguments to pass to the superclass initializer.
        **kwargs: Additional keyword arguments to pass to the superclass initializer.
        
        Returns:
        None: This function does not return any value.
        """

        super().__init__(*args, **kwargs)
        self.start = start
        self.end = end

    def as_sql(self, compiler, connection):
        lhs, params = compiler.compile(self.lhs)
        return '%s[%%s:%%s]' % lhs, params + [self.start, self.end]


class SliceTransformFactory:

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __call__(self, *args, **kwargs):
        return SliceTransform(self.start, self.end, *args, **kwargs)
