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
        """
        The `deconstruct` method is a utility function used in Django models to provide a way to serialize a model field or constraint into a tuple that can be used to reconstruct the field or constraint. This method is particularly useful for custom fields or constraints that need to be properly serialized and deserialized.
        
        ### Parameters:
        - `self`: The instance of the class that is being deconstructed.
        
        ### Returns:
        - A tuple containing:
        - `path` (str): The fully qualified path to the class
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
        super().__init__(name)

    def _get_check_sql(self, model, schema_editor):
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
        """
        __eq__(self, other)
        
        Compares two CheckConstraint objects for equality.
        
        Parameters:
        - other (CheckConstraint): The other CheckConstraint object to compare with.
        
        Returns:
        - bool: True if the two CheckConstraint objects are equal (same name and check condition), False otherwise.
        
        This method checks if the provided 'other' object is an instance of CheckConstraint and then compares its name and check condition with the current object's attributes.
        """

        return (
            isinstance(other, CheckConstraint) and
            self.name == other.name and
            self.check == other.check
        )

    def deconstruct(self):
        path, args, kwargs = super().deconstruct()
        kwargs['check'] = self.check
        return path, args, kwargs


class UniqueConstraint(BaseConstraint):
    def __init__(self, *, fields, name, condition=None):
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
        return (
            isinstance(other, UniqueConstraint) and
            self.name == other.name and
            self.fields == other.fields and
            self.condition == other.condition
        )

    def deconstruct(self):
        path, args, kwargs = super().deconstruct()
        kwargs['fields'] = self.fields
        if self.condition:
            kwargs['condition'] = self.condition
        return path, args, kwargs
] = self.condition
        return path, args, kwargs
