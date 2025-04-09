"""
This Python file defines classes for managing database constraints in Django models. It includes:
- **BaseConstraint**: An abstract base class for defining generic constraints.
- **CheckConstraint**: A concrete implementation for defining check constraints.
- **Deferrable**: An enumeration for specifying whether constraints can be deferred.
- **UniqueConstraint**: A concrete implementation for defining unique constraints.

Each class provides methods for generating SQL statements to create, remove, and represent constraints. The interactions between these classes involve creating, modifying, and deleting constraints on Django models through SQL commands. ```python
"""
"""
This Python file defines classes for managing database constraints in Django models. It includes:
- **BaseConstraint**: An abstract base class for defining generic constraints.
- **CheckConstraint**: A concrete implementation for defining check constraints.
- **Deferrable**: An enumeration for specifying whether constraints can be deferred.
- **UniqueConstraint**: A concrete implementation for defining unique constraints.

Each class provides methods for generating SQL statements to create, remove, and represent constraints. The interactions between these classes involve creating, modifying, and deleting constraints on Django models through SQL commands. ```python
"""
"""
This Python file defines classes for managing database constraints in Django models. It includes:
- **BaseConstraint**: An abstract base class for defining generic constraints.
- **CheckConstraint**: A concrete implementation for defining check constraints.
- **Deferrable**: An enumeration for specifying whether constraints can be deferred.
- **UniqueConstraint**: A concrete implementation for defining unique constraints.

Each class provides methods for generating SQL statements to create, remove, and represent constraints. The interactions between these classes involve creating, modifying, and deleting constraints on Django models through SQL commands. ```python
"""
"""
The provided Python file defines several classes related to database constraints in Django models. It includes:

- **BaseConstraint**: An abstract base class for defining constraints on Django models. It provides common methods for creating, removing, and representing constraints.
  
- **CheckConstraint**: A concrete implementation of `BaseConstraint` for defining check constraints. These constraints enforce specific conditions on the data in the database.

- **Deferrable**: An enumeration class that defines whether a constraint can be deferred or must be immediate.

- **UniqueConstraint**: Another concrete implementation of `BaseConstraint` for defining unique constraints. These constraints ensure that certain fields or expressions do not contain duplicate values.

Each class has methods for generating SQL statements to create, remove, and represent the constraints.
"""
from enum import Enum

from django.db.models.expressions import ExpressionList, F
from django.db.models.indexes import IndexExpression
from django.db.models.query_utils import Q
from django.db.models.sql.query import Query

__all__ = ['CheckConstraint', 'Deferrable', 'UniqueConstraint']


class BaseConstraint:
    def __init__(self, name):
        self.name = name

    @property
    def contains_expressions(self):
        return False

    def constraint_sql(self, model, schema_editor):
        raise NotImplementedError('This method must be implemented by a subclass.')

    def create_sql(self, model, schema_editor):
        raise NotImplementedError('This method must be implemented by a subclass.')

    def remove_sql(self, model, schema_editor):
        raise NotImplementedError('This method must be implemented by a subclass.')

    def deconstruct(self):
        """
        Deconstructs the constraint object into its key components.
        
        Args:
        None
        
        Returns:
        tuple: A tuple containing the path of the constraint class, an empty tuple, and a dictionary with the constraint's name.
        
        Summary:
        This function takes a Django model constraint object and returns a deconstructed representation of it. The path of the constraint class is obtained by replacing the module name 'django.db.models.constraints' with 'django.db.models'. The returned tuple consists of the modified path
        """

        path = '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
        path = path.replace('django.db.models.constraints', 'django.db.models')
        return (path, (), {'name': self.name})

    def clone(self):
        _, args, kwargs = self.deconstruct()
        return self.__class__(*args, **kwargs)


class CheckConstraint(BaseConstraint):
    def __init__(self, *, check, name):
        """
        Initialize a CheckConstraint object.
        
        Args:
        check (Q instance or boolean expression): The condition that the
        constraint checks.
        name (str): The name of the constraint.
        
        Raises:
        TypeError: If `check` is not a Q instance or boolean expression.
        
        This method initializes a CheckConstraint object with a given condition
        and name. It ensures that the provided condition is either a Q instance
        or a boolean expression by checking the presence of the `conditional`
        """

        self.check = check
        if not getattr(check, 'conditional', False):
            raise TypeError(
                'CheckConstraint.check must be a Q instance or boolean '
                'expression.'
            )
        super().__init__(name)

    def _get_check_sql(self, model, schema_editor):
        """
        Generates a SQL query to check constraints on a given model.
        
        Args:
        model (Model): The Django model to generate the check constraint for.
        schema_editor (SchemaEditor): The schema editor to use for quoting values.
        
        Returns:
        str: The generated SQL query with quoted parameters.
        
        Important Functions:
        - `Query`: Constructs the query for the given model.
        - `build_where`: Builds the WHERE clause of the query based on the provided check condition.
        -
        """

        query = Query(model=model, alias_cols=False)
        where = query.build_where(self.check)
        compiler = query.get_compiler(connection=schema_editor.connection)
        sql, params = where.as_sql(compiler, schema_editor.connection)
        return sql % tuple(schema_editor.quote_value(p) for p in params)

    def constraint_sql(self, model, schema_editor):
        check = self._get_check_sql(model, schema_editor)
        return schema_editor._check_sql(self.name, check)

    def create_sql(self, model, schema_editor):
        check = self._get_check_sql(model, schema_editor)
        return schema_editor._create_check_sql(model, self.name, check)

    def remove_sql(self, model, schema_editor):
        return schema_editor._delete_check_sql(model, self.name)

    def __repr__(self):
        """
        Return a string representation of the object, formatted as '<ClassName: check=<CheckValue> name=<NameValue>>'. The function takes no arguments and returns a string.
        
        Args:
        None
        
        Returns:
        str: A string representation of the object.
        
        Attributes:
        check (str): The check value associated with the object.
        name (str): The name value associated with the object.
        
        Example:
        >>> obj = SomeClass(check='valid', name='example')
        """

        return '<%s: check=%s name=%s>' % (
            self.__class__.__qualname__,
            self.check,
            repr(self.name),
        )

    def __eq__(self, other):
        """
        Check if two CheckConstraint objects are equal.
        
        This method compares two CheckConstraint objects for equality based on their names and check conditions. It first checks if the other object is an instance of CheckConstraint, and if so, compares the names and check conditions. If not, it falls back to the default equality comparison using the superclass's implementation.
        
        Args:
        other (CheckConstraint): The other CheckConstraint object to compare with.
        
        Returns:
        bool: True if both objects have the same
        """

        if isinstance(other, CheckConstraint):
            return self.name == other.name and self.check == other.check
        return super().__eq__(other)

    def deconstruct(self):
        """
        Deconstructs the current object into its component parts.
        
        This method is used to break down the object into its constituent parts, specifically the path, arguments (args), and keyword arguments (kwargs). The original `super().deconstruct()` method is called to get the initial components, and then the 'check' attribute of the current object is added to the keyword arguments.
        
        Args:
        None
        
        Returns:
        tuple: A tuple containing the path, arguments, and keyword arguments of
        """

        path, args, kwargs = super().deconstruct()
        kwargs['check'] = self.check
        return path, args, kwargs


class Deferrable(Enum):
    DEFERRED = 'deferred'
    IMMEDIATE = 'immediate'

    # A similar format was proposed for Python 3.10.
    def __repr__(self):
        return f'{self.__class__.__qualname__}.{self._name_}'


class UniqueConstraint(BaseConstraint):
    def __init__(
        """
        Initialize a UniqueConstraint object.
        
        Args:
        *expressions: Expressions to be included in the unique constraint.
        fields: Fields to be included in the unique constraint.
        name: Name of the unique constraint.
        condition: Condition to be applied to the unique constraint.
        deferrable: Whether the unique constraint can be deferred.
        include: Fields to be included in the unique constraint.
        opclasses: Operator classes to be used for the unique constraint.
        
        Raises:
        """

        self,
        *expressions,
        fields=(),
        name=None,
        condition=None,
        deferrable=None,
        include=None,
        opclasses=(),
    ):
        if not name:
            raise ValueError('A unique constraint must be named.')
        if not expressions and not fields:
            raise ValueError(
                'At least one field or expression is required to define a '
                'unique constraint.'
            )
        if expressions and fields:
            raise ValueError(
                'UniqueConstraint.fields and expressions are mutually exclusive.'
            )
        if not isinstance(condition, (type(None), Q)):
            raise ValueError('UniqueConstraint.condition must be a Q instance.')
        if condition and deferrable:
            raise ValueError(
                'UniqueConstraint with conditions cannot be deferred.'
            )
        if include and deferrable:
            raise ValueError(
                'UniqueConstraint with include fields cannot be deferred.'
            )
        if opclasses and deferrable:
            raise ValueError(
                'UniqueConstraint with opclasses cannot be deferred.'
            )
        if expressions and deferrable:
            raise ValueError(
                'UniqueConstraint with expressions cannot be deferred.'
            )
        if expressions and opclasses:
            raise ValueError(
                'UniqueConstraint.opclasses cannot be used with expressions. '
                'Use django.contrib.postgres.indexes.OpClass() instead.'
            )
        if not isinstance(deferrable, (type(None), Deferrable)):
            raise ValueError(
                'UniqueConstraint.deferrable must be a Deferrable instance.'
            )
        if not isinstance(include, (type(None), list, tuple)):
            raise ValueError('UniqueConstraint.include must be a list or tuple.')
        if not isinstance(opclasses, (list, tuple)):
            raise ValueError('UniqueConstraint.opclasses must be a list or tuple.')
        if opclasses and len(fields) != len(opclasses):
            raise ValueError(
                'UniqueConstraint.fields and UniqueConstraint.opclasses must '
                'have the same number of elements.'
            )
        self.fields = tuple(fields)
        self.condition = condition
        self.deferrable = deferrable
        self.include = tuple(include) if include else ()
        self.opclasses = opclasses
        self.expressions = tuple(
            F(expression) if isinstance(expression, str) else expression
            for expression in expressions
        )
        super().__init__(name)

    @property
    def contains_expressions(self):
        return bool(self.expressions)

    def _get_condition_sql(self, model, schema_editor):
        if self.condition is None:
            return None
        query = Query(model=model, alias_cols=False)
        where = query.build_where(self.condition)
        compiler = query.get_compiler(connection=schema_editor.connection)
        sql, params = where.as_sql(compiler, schema_editor.connection)
        return sql % tuple(schema_editor.quote_value(p) for p in params)

    def _get_index_expressions(self, model, schema_editor):
        if not self.expressions:
            return None
        index_expressions = []
        for expression in self.expressions:
            index_expression = IndexExpression(expression)
            index_expression.set_wrapper_classes(schema_editor.connection)
            index_expressions.append(index_expression)
        return ExpressionList(*index_expressions).resolve_expression(
            Query(model, alias_cols=False),
        )

    def constraint_sql(self, model, schema_editor):
        fields = [model._meta.get_field(field_name) for field_name in self.fields]
        include = [model._meta.get_field(field_name).column for field_name in self.include]
        condition = self._get_condition_sql(model, schema_editor)
        expressions = self._get_index_expressions(model, schema_editor)
        return schema_editor._unique_sql(
            model, fields, self.name, condition=condition,
            deferrable=self.deferrable, include=include,
            opclasses=self.opclasses, expressions=expressions,
        )

    def create_sql(self, model, schema_editor):
        fields = [model._meta.get_field(field_name) for field_name in self.fields]
        include = [model._meta.get_field(field_name).column for field_name in self.include]
        condition = self._get_condition_sql(model, schema_editor)
        expressions = self._get_index_expressions(model, schema_editor)
        return schema_editor._create_unique_sql(
            model, fields, self.name, condition=condition,
            deferrable=self.deferrable, include=include,
            opclasses=self.opclasses, expressions=expressions,
        )

    def remove_sql(self, model, schema_editor):
        condition = self._get_condition_sql(model, schema_editor)
        include = [model._meta.get_field(field_name).column for field_name in self.include]
        expressions = self._get_index_expressions(model, schema_editor)
        return schema_editor._delete_unique_sql(
            model, self.name, condition=condition, deferrable=self.deferrable,
            include=include, opclasses=self.opclasses, expressions=expressions,
        )

    def __repr__(self):
        return '<%s:%s%s%s%s%s%s%s>' % (
            self.__class__.__qualname__,
            '' if not self.fields else ' fields=%s' % repr(self.fields),
            '' if not self.expressions else ' expressions=%s' % repr(self.expressions),
            ' name=%s' % repr(self.name),
            '' if self.condition is None else ' condition=%s' % self.condition,
            '' if self.deferrable is None else ' deferrable=%r' % self.deferrable,
            '' if not self.include else ' include=%s' % repr(self.include),
            '' if not self.opclasses else ' opclasses=%s' % repr(self.opclasses),
        )

    def __eq__(self, other):
        if isinstance(other, UniqueConstraint):
            return (
                self.name == other.name and
                self.fields == other.fields and
                self.condition == other.condition and
                self.deferrable == other.deferrable and
                self.include == other.include and
                self.opclasses == other.opclasses and
                self.expressions == other.expressions
            )
        return super().__eq__(other)

    def deconstruct(self):
        path, args, kwargs = super().deconstruct()
        if self.fields:
            kwargs['fields'] = self.fields
        if self.condition:
            kwargs['condition'] = self.condition
        if self.deferrable:
            kwargs['deferrable'] = self.deferrable
        if self.include:
            kwargs['include'] = self.include
        if self.opclasses:
            kwargs['opclasses'] = self.opclasses
        return path, self.expressions, kwargs
