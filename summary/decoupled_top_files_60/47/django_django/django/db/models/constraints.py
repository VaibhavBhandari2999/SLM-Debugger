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
        Deconstructs a model constraint into a path, arguments, and keyword arguments.
        
        This function is used to serialize a model constraint object for storage or transmission. It returns a tuple containing the path to the constraint's class, an empty tuple for positional arguments, and a dictionary for keyword arguments. The path is adjusted to replace the 'django.db.models.constraints' module with 'django.db.models' for compatibility.
        
        Parameters:
        self (ModelConstraint): The model constraint object to deconstruct.
        
        Returns:
        """

        path = '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
        path = path.replace('django.db.models.constraints', 'django.db.models')
        return (path, (), {'name': self.name})

    def clone(self):
        _, args, kwargs = self.deconstruct()
        return self.__class__(*args, **kwargs)


class CheckConstraint(BaseConstraint):
    def __init__(self, *, check, name):
        self.check = check
        if not getattr(check, 'conditional', False):
            raise TypeError(
                'CheckConstraint.check must be a Q instance or boolean '
                'expression.'
            )
        super().__init__(name)

    def _get_check_sql(self, model, schema_editor):
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
        __eq__(self, other)
        
        Compares the current instance with another object to determine if they are equal.
        
        Parameters:
        - other (CheckConstraint): The object to compare with the current instance.
        
        Returns:
        - bool: True if the current instance and the other object are equal, False otherwise. Two CheckConstraint instances are considered equal if they have the same name and check expression. If the other object is not a CheckConstraint, the comparison is delegated to the superclass's __eq__ method.
        """

        if isinstance(other, CheckConstraint):
            return self.name == other.name and self.check == other.check
        return super().__eq__(other)

    def deconstruct(self):
        path, args, kwargs = super().deconstruct()
        kwargs['check'] = self.check
        return path, args, kwargs


class Deferrable(Enum):
    DEFERRED = 'deferred'
    IMMEDIATE = 'immediate'


class UniqueConstraint(BaseConstraint):
    def __init__(self, *, fields, name, condition=None, deferrable=None, include=None):
        if not fields:
            raise ValueError('At least one field is required to define a unique constraint.')
        if not isinstance(condition, (type(None), Q)):
            raise ValueError('UniqueConstraint.condition must be a Q instance.')
        if condition and deferrable:
            raise ValueError(
                'UniqueConstraint with conditions cannot be deferred.'
            )
        if not isinstance(deferrable, (type(None), Deferrable)):
            raise ValueError(
                'UniqueConstraint.deferrable must be a Deferrable instance.'
            )
        if not isinstance(include, (type(None), list, tuple)):
            raise ValueError('UniqueConstraint.include must be a list or tuple.')
        self.fields = tuple(fields)
        self.condition = condition
        self.deferrable = deferrable
        self.include = tuple(include) if include else ()
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
        """
        Generates a SQL constraint for a Django model.
        
        This function creates a unique constraint for a Django model based on specified fields. It also supports additional fields to be included in the constraint.
        
        Parameters:
        model (django.db.models.Model): The Django model for which the constraint is being created.
        schema_editor (django.db.backends.base.schema.BaseSchemaEditor): The schema editor used to execute the constraint creation.
        
        Returns:
        str: The SQL statement for creating the unique constraint.
        
        Key Parameters:
        -
        """

        fields = [model._meta.get_field(field_name).column for field_name in self.fields]
        include = [model._meta.get_field(field_name).column for field_name in self.include]
        condition = self._get_condition_sql(model, schema_editor)
        return schema_editor._unique_sql(
            model, fields, self.name, condition=condition,
            deferrable=self.deferrable, include=include,
        )

    def create_sql(self, model, schema_editor):
        fields = [model._meta.get_field(field_name).column for field_name in self.fields]
        include = [model._meta.get_field(field_name).column for field_name in self.include]
        condition = self._get_condition_sql(model, schema_editor)
        return schema_editor._create_unique_sql(
            model, fields, self.name, condition=condition,
            deferrable=self.deferrable, include=include,
        )

    def remove_sql(self, model, schema_editor):
        """
        Remove a unique constraint from a model.
        
        This function is used to remove a unique constraint from a Django model.
        
        Parameters:
        model (django.db.models.Model): The Django model from which the unique constraint will be removed.
        schema_editor (django.db.migrations.operations.base.Operation): The schema editor to use for executing the SQL.
        
        Returns:
        str: The SQL statement to remove the unique constraint.
        
        Key Parameters:
        - `model`: The model from which the unique constraint is to be removed.
        """

        condition = self._get_condition_sql(model, schema_editor)
        include = [model._meta.get_field(field_name).column for field_name in self.include]
        return schema_editor._delete_unique_sql(
            model, self.name, condition=condition, deferrable=self.deferrable,
            include=include,
        )

    def __repr__(self):
        return '<%s: fields=%r name=%r%s%s%s>' % (
            self.__class__.__name__, self.fields, self.name,
            '' if self.condition is None else ' condition=%s' % self.condition,
            '' if self.deferrable is None else ' deferrable=%s' % self.deferrable,
            '' if not self.include else ' include=%s' % repr(self.include),
        )

    def __eq__(self, other):
        """
        Method to check if the current instance is equal to another object.
        
        Parameters:
        other (UniqueConstraint): The object to compare with the current instance.
        
        Returns:
        bool: True if the current instance is equal to the other object, False otherwise.
        
        Notes:
        - The comparison is based on the following attributes: `name`, `fields`, `condition`, `deferrable`, and `include`.
        - If `other` is not an instance of `UniqueConstraint
        """

        if isinstance(other, UniqueConstraint):
            return (
                self.name == other.name and
                self.fields == other.fields and
                self.condition == other.condition and
                self.deferrable == other.deferrable and
                self.include == other.include
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
        return path, args, kwargs
