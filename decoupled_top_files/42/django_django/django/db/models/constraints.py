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
    def __init__(self, *, fields, name, condition=None, deferrable=None):
        """
        Initialize a UniqueConstraint object.
        
        Args:
        fields (tuple): A tuple of field names that define the unique constraint.
        name (str): The name of the unique constraint.
        condition (Q, optional): A Q instance representing an additional condition for the unique constraint. Defaults to None.
        deferrable (Deferrable, optional): A Deferrable instance indicating whether the constraint can be deferred. Defaults to None.
        
        Raises:
        ValueError: If no fields are provided or
        """

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
        self.fields = tuple(fields)
        self.condition = condition
        self.deferrable = deferrable
        super().__init__(name)

    def _get_condition_sql(self, model, schema_editor):
        """
        Generates SQL condition based on the given model and schema editor.
        
        Args:
        model (Model): The Django model to generate the condition for.
        schema_editor (SchemaEditor): The schema editor to use for quoting values.
        
        Returns:
        str: The generated SQL condition or None if no condition is specified.
        """

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
        
        Args:
        model (django.db.models.Model): The Django model to which the constraint will be applied.
        schema_editor (django.db.models.sql.compiler.SQLCompiler): The schema editor used to generate the SQL.
        
        Returns:
        str: The generated SQL constraint.
        
        This function constructs a SQL constraint based on the specified fields of the given Django model. It uses the provided `schema_editor` to generate the unique SQL constraint and applies any necessary
        """

        fields = [model._meta.get_field(field_name).column for field_name in self.fields]
        condition = self._get_condition_sql(model, schema_editor)
        return schema_editor._unique_sql(
            model, fields, self.name, condition=condition,
            deferrable=self.deferrable,
        )

    def create_sql(self, model, schema_editor):
        """
        Creates a unique SQL constraint for a Django model.
        
        Args:
        model (django.db.models.Model): The Django model to which the unique constraint will be applied.
        schema_editor (django.db.migrations.operations.base.OperationSchemaEditor): The schema editor used to generate the SQL.
        
        Returns:
        str: The generated SQL statement for creating a unique constraint.
        
        Important Functions:
        - `model._meta.get_field(field_name).column`: Retrieves the column name of a field in the model.
        """

        fields = [model._meta.get_field(field_name).column for field_name in self.fields]
        condition = self._get_condition_sql(model, schema_editor)
        return schema_editor._create_unique_sql(
            model, fields, self.name, condition=condition,
            deferrable=self.deferrable,
        )

    def remove_sql(self, model, schema_editor):
        """
        Removes a unique constraint from a database table.
        
        Args:
        model (Model): The Django model representing the table.
        schema_editor (SchemaEditor): The schema editor object used to execute the SQL command.
        
        Returns:
        str: The SQL command to remove the unique constraint.
        """

        condition = self._get_condition_sql(model, schema_editor)
        return schema_editor._delete_unique_sql(
            model, self.name, condition=condition, deferrable=self.deferrable,
        )

    def __repr__(self):
        """
        Generate a string representation of the object.
        
        Args:
        None (The function does not take any arguments).
        
        Returns:
        str: A formatted string representing the object's attributes.
        
        Attributes:
        fields (list): The fields of the object.
        name (str): The name of the object.
        condition (str, optional): The condition associated with the object.
        deferrable (bool, optional): Whether the object is deferrable or not.
        
        Example:
        >>>
        """

        return '<%s: fields=%r name=%r%s%s>' % (
            self.__class__.__name__, self.fields, self.name,
            '' if self.condition is None else ' condition=%s' % self.condition,
            '' if self.deferrable is None else ' deferrable=%s' % self.deferrable,
        )

    def __eq__(self, other):
        """
        Compares two `UniqueConstraint` objects for equality.
        
        This method checks if the given `other` object is an instance of `UniqueConstraint` and then compares its attributes: `name`, `fields`, `condition`, and `deferrable`. If all these attributes match, the objects are considered equal. Otherwise, it calls the `__eq__` method from the superclass.
        
        Args:
        other (UniqueConstraint): The object to compare with.
        
        Returns:
        bool
        """

        if isinstance(other, UniqueConstraint):
            return (
                self.name == other.name and
                self.fields == other.fields and
                self.condition == other.condition and
                self.deferrable == other.deferrable
            )
        return super().__eq__(other)

    def deconstruct(self):
        """
        Deconstructs the object into its constituent parts.
        
        This method is used to break down the object into its fundamental components, specifically the path, arguments, and keyword arguments. It also includes additional parameters such as `fields`, `condition`, and `deferrable` which are specific to this implementation.
        
        Args:
        None (This method is called automatically by Django's serialization framework)
        
        Returns:
        tuple: A tuple containing the path, arguments, and keyword arguments of the object. The
        """

        path, args, kwargs = super().deconstruct()
        kwargs['fields'] = self.fields
        if self.condition:
            kwargs['condition'] = self.condition
        if self.deferrable:
            kwargs['deferrable'] = self.deferrable
        return path, args, kwargs
