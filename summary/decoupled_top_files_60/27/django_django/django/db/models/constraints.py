from django.db.models.query_utils import Q
from django.db.models.sql.query import Query

__all__ = ['CheckConstraint', 'UniqueConstraint']


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
        path = '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
        path = path.replace('django.db.models.constraints', 'django.db.models')
        return (path, (), {'name': self.name})

    def clone(self):
        _, args, kwargs = self.deconstruct()
        return self.__class__(*args, **kwargs)


class CheckConstraint(BaseConstraint):
    def __init__(self, *, check, name):
        self.check = check
        super().__init__(name)

    def _get_check_sql(self, model, schema_editor):
        """
        Generates a SQL query to check a condition on a model.
        
        This function constructs a SQL query to check a specific condition on a given model using a provided check. The query is built using a Query object and a Where object, which are responsible for generating the WHERE clause of the SQL query. The query is then compiled using a compiler object specific to the database connection.
        
        Parameters:
        model (Model): The Django model class to which the check applies.
        schema_editor (SchemaEditor): An object
        """

        query = Query(model=model)
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
        if isinstance(other, CheckConstraint):
            return self.name == other.name and self.check == other.check
        return super().__eq__(other)

    def deconstruct(self):
        path, args, kwargs = super().deconstruct()
        kwargs['check'] = self.check
        return path, args, kwargs


class UniqueConstraint(BaseConstraint):
    def __init__(self, *, fields, name, condition=None):
        """
        Initialize a UniqueConstraint instance.
        
        Args:
        fields (tuple): A tuple of field names that define the unique constraint.
        name (str): The name of the unique constraint.
        condition (Optional[Q], optional): A Q object that defines a condition for the unique constraint. Defaults to None.
        
        Raises:
        ValueError: If no fields are provided or if the condition is not a Q instance.
        
        This method initializes a UniqueConstraint object with the specified fields and name. It also allows for an
        """

        if not fields:
            raise ValueError('At least one field is required to define a unique constraint.')
        if not isinstance(condition, (type(None), Q)):
            raise ValueError('UniqueConstraint.condition must be a Q instance.')
        self.fields = tuple(fields)
        self.condition = condition
        super().__init__(name)

    def _get_condition_sql(self, model, schema_editor):
        if self.condition is None:
            return None
        query = Query(model=model)
        where = query.build_where(self.condition)
        compiler = query.get_compiler(connection=schema_editor.connection)
        sql, params = where.as_sql(compiler, schema_editor.connection)
        return sql % tuple(schema_editor.quote_value(p) for p in params)

    def constraint_sql(self, model, schema_editor):
        """
        Generates a SQL constraint for a Django model.
        
        This function is used to create a unique constraint on specified fields in a Django model. It constructs the necessary SQL command to enforce uniqueness based on the provided fields and condition.
        
        Parameters:
        model (django.db.models.Model): The Django model class on which the constraint is to be applied.
        schema_editor (django.db.backends.base.schema.BaseSchemaEditor): The schema editor object used to execute the SQL command.
        
        Returns:
        str: The SQL command to
        """

        fields = [model._meta.get_field(field_name).column for field_name in self.fields]
        condition = self._get_condition_sql(model, schema_editor)
        return schema_editor._unique_sql(model, fields, self.name, condition=condition)

    def create_sql(self, model, schema_editor):
        fields = [model._meta.get_field(field_name).column for field_name in self.fields]
        condition = self._get_condition_sql(model, schema_editor)
        return schema_editor._create_unique_sql(model, fields, self.name, condition=condition)

    def remove_sql(self, model, schema_editor):
        condition = self._get_condition_sql(model, schema_editor)
        return schema_editor._delete_unique_sql(model, self.name, condition=condition)

    def __repr__(self):
        return '<%s: fields=%r name=%r%s>' % (
            self.__class__.__name__, self.fields, self.name,
            '' if self.condition is None else ' condition=%s' % self.condition,
        )

    def __eq__(self, other):
        """
        Method to check if the current instance is equal to another object.
        
        Parameters:
        - other (UniqueConstraint): The object to compare with the current instance.
        
        Returns:
        - bool: True if the current instance is equal to the other object, False otherwise.
        
        This method is used to determine equality between instances of the UniqueConstraint class. It checks if the 'name', 'fields', and 'condition' attributes of the current instance match those of the provided 'other' object. If the 'other'
        """

        if isinstance(other, UniqueConstraint):
            return (
                self.name == other.name and
                self.fields == other.fields and
                self.condition == other.condition
            )
        return super().__eq__(other)

    def deconstruct(self):
        """
        Deconstructs the current object into its component parts for serialization or migration purposes.
        
        This method is typically used in Django model fields to ensure that the field's configuration can be properly serialized and later reconstructed.
        
        Parameters:
        None (This method is called internally by Django and does not take any explicit parameters).
        
        Returns:
        A tuple containing:
        - `path` (str): The path to the current class.
        - `args` (tuple): Positional arguments required to reconstruct the object.
        """

        path, args, kwargs = super().deconstruct()
        kwargs['fields'] = self.fields
        if self.condition:
            kwargs['condition'] = self.condition
        return path, args, kwargs
s
