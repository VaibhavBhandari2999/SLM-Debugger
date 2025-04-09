"""
This Python file defines classes for handling database constraints in Django models. It includes:

- `BaseConstraint`: A base class for defining constraints, providing methods for generating SQL for creating, removing, and cloning constraints. It also includes a `deconstruct` method for serialization during migrations.

- `CheckConstraint`: A subclass of `BaseConstraint` for defining check constraints. It requires a condition (a `Q` instance or boolean expression) and a name. It generates SQL for checking the condition on a model.

- `UniqueConstraint`: Another subclass of `BaseConstraint` for defining unique constraints. It allows specifying fields, a condition, whether the constraint is deferrable, and additional fields to include in the constraint. It generates SQL for creating and
"""
"""
This Python file defines classes for handling database constraints in Django models. It includes:

- `BaseConstraint`: A base class for defining constraints, providing methods for generating SQL for creating, removing, and cloning constraints. It also includes a `deconstruct` method for serialization during migrations.
  
- `CheckConstraint`: A subclass of `BaseConstraint` for defining check constraints. It requires a condition (a `Q` instance or boolean expression) and a name. It generates SQL for checking the condition on a model.

- `UniqueConstraint`: Another subclass of `BaseConstraint` for defining unique constraints. It allows specifying fields, a condition, whether the constraint is deferrable, and additional fields to include in the constraint. It generates SQL for creating
"""
"""
This Python file defines classes for handling database constraints in Django models. It includes:

- `BaseConstraint`: A base class for defining constraints, providing methods for generating SQL for creating, removing, and cloning constraints. It also includes a `deconstruct` method for serialization during migrations.
  
- `CheckConstraint`: A subclass of `BaseConstraint` for defining check constraints. It requires a condition (a `Q` instance or boolean expression) and a name. It generates SQL for checking the condition on a model.

- `UniqueConstraint`: Another subclass of `BaseConstraint` for defining unique constraints. It allows specifying fields, a condition, whether the constraint is deferrable, and additional fields to include in the constraint. It generates SQL for creating
"""
"""
The provided Python file contains definitions for database constraints in Django models. It includes three main classes: `BaseConstraint`, `CheckConstraint`, and `UniqueConstraint`. 

- `BaseConstraint` serves as a base class for defining constraints. It provides methods for generating SQL for creating, removing, and cloning constraints. The `deconstruct` method is used to serialize the constraint object for migrations.

- `CheckConstraint` extends `BaseConstraint` to handle check constraints. It requires a condition (a `Q` instance or boolean expression) and a name. It generates SQL for checking the condition on a model.

- `UniqueConstraint` also extends `BaseConstraint` and handles unique constraints. It allows specifying fields, a condition, whether the constraint is
"""
from enum import Enum

from django.db.models.query_utils import Q
from django.db.models.sql.query import Query

__all__ = ['CheckConstraint', 'Deferrable', 'UniqueConstraint']


class BaseConstraint:
    def __init__(self, name):
        self.name = name

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
        return "<%s: check='%s' name=%r>" % (self.__class__.__name__, self.check, self.name)

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


class UniqueConstraint(BaseConstraint):
    def __init__(
        """
        Initialize a UniqueConstraint object.
        
        Args:
        fields (tuple): The fields that make up the unique constraint.
        name (str): The name of the unique constraint.
        condition (Q, optional): A condition to apply to the unique constraint. Defaults to None.
        deferrable (Deferrable, optional): Whether the constraint can be deferred. Defaults to None.
        include (list or tuple, optional): Fields to include in the constraint. Defaults to None.
        opclasses
        """

        self,
        *,
        fields,
        name,
        condition=None,
        deferrable=None,
        include=None,
        opclasses=(),
    ):
        if not fields:
            raise ValueError('At least one field is required to define a unique constraint.')
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
        super().__init__(name)

    def _get_condition_sql(self, model, schema_editor):
        if self.condition is None:
            return None
        query = Query(model=model, alias_cols=False)
        where = query.build_where(self.condition)
        compiler = query.get_compiler(connection=schema_editor.connection)
        sql, params = where.as_sql(compiler, schema_editor.connection)
        return sql % tuple(schema_editor.quote_value(p) for p in params)

    def constraint_sql(self, model, schema_editor):
        fields = [model._meta.get_field(field_name).column for field_name in self.fields]
        include = [model._meta.get_field(field_name).column for field_name in self.include]
        condition = self._get_condition_sql(model, schema_editor)
        return schema_editor._unique_sql(
            model, fields, self.name, condition=condition,
            deferrable=self.deferrable, include=include,
            opclasses=self.opclasses,
        )

    def create_sql(self, model, schema_editor):
        fields = [model._meta.get_field(field_name).column for field_name in self.fields]
        include = [model._meta.get_field(field_name).column for field_name in self.include]
        condition = self._get_condition_sql(model, schema_editor)
        return schema_editor._create_unique_sql(
            model, fields, self.name, condition=condition,
            deferrable=self.deferrable, include=include,
            opclasses=self.opclasses,
        )

    def remove_sql(self, model, schema_editor):
        condition = self._get_condition_sql(model, schema_editor)
        include = [model._meta.get_field(field_name).column for field_name in self.include]
        return schema_editor._delete_unique_sql(
            model, self.name, condition=condition, deferrable=self.deferrable,
            include=include, opclasses=self.opclasses,
        )

    def __repr__(self):
        return '<%s: fields=%r name=%r%s%s%s%s>' % (
            self.__class__.__name__, self.fields, self.name,
            '' if self.condition is None else ' condition=%s' % self.condition,
            '' if self.deferrable is None else ' deferrable=%s' % self.deferrable,
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
                self.opclasses == other.opclasses
            )
        return super().__eq__(other)

    def deconstruct(self):
        path, args, kwargs = super().deconstruct()
        kwargs['fields'] = self.fields
        if self.condition:
            kwargs['condition'] = self.condition
        if self.deferrable:
            kwargs['deferrable'] = self.deferrable
        if self.include:
            kwargs['include'] = self.include
        if self.opclasses:
            kwargs['opclasses'] = self.opclasses
        return path, args, kwargs
