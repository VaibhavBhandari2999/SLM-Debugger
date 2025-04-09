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
        self.check = check
        super().__init__(name)

    def _get_check_sql(self, model, schema_editor):
        """
        Generates a SQL query to check a condition on a given model.
        
        Args:
        model (Model): The Django model to generate the query for.
        schema_editor (SchemaEditor): The schema editor to use for quoting values.
        
        Returns:
        str: The generated SQL query with parameters quoted by the schema editor.
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
        """
        Check if two CheckConstraint objects are equal.
        
        Args:
        other (CheckConstraint): The other CheckConstraint object to compare with.
        
        Returns:
        bool: True if both CheckConstraint objects have the same name and check expression, False otherwise.
        
        Notes:
        - This method compares the `name` and `check` attributes of the two CheckConstraint objects.
        - It uses the `isinstance` function to ensure that the `other` object is also an instance of CheckConstraint.
        """

        return (
            isinstance(other, CheckConstraint) and
            self.name == other.name and
            self.check == other.check
        )

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


class UniqueConstraint(BaseConstraint):
    def __init__(self, *, fields, name, condition=None):
        """
        Initialize a UniqueConstraint object.
        
        Args:
        fields (tuple): A tuple of field names that define the unique constraint.
        name (str): The name of the unique constraint.
        condition (Optional[Q]): An optional Q instance that defines an additional condition for the unique constraint.
        
        Raises:
        ValueError: If no fields are provided or if the condition is not a Q instance.
        
        Attributes:
        fields (tuple): The field names that define the unique constraint.
        condition (Optional
        """

        if not fields:
            raise ValueError('At least one field is required to define a unique constraint.')
        if not isinstance(condition, (type(None), Q)):
            raise ValueError('UniqueConstraint.condition must be a Q instance.')
        self.fields = tuple(fields)
        self.condition = condition
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
        query = Query(model=model)
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
        
        This function constructs a unique SQL constraint for the specified model based on the given fields and condition. It uses the provided schema editor to generate the necessary SQL and returns the resulting constraint
        """

        fields = [model._meta.get_field(field_name).column for field_name in self.fields]
        condition = self._get_condition_sql(model, schema_editor)
        return schema_editor._unique_sql(model, fields, self.name, condition=condition)

    def create_sql(self, model, schema_editor):
        """
        Creates a unique SQL constraint for a Django model.
        
        Args:
        model (django.db.models.Model): The Django model for which the unique constraint is being created.
        schema_editor (django.db.migrations.operations.base.OperationSchemaEditor): The schema editor used to generate the SQL.
        
        Returns:
        str: The generated SQL statement for creating a unique constraint.
        
        Important Functions:
        - `model._meta.get_field(field_name).column`: Retrieves the column name of a field in the model.
        """

        fields = [model._meta.get_field(field_name).column for field_name in self.fields]
        condition = self._get_condition_sql(model, schema_editor)
        return schema_editor._create_unique_sql(model, fields, self.name, condition=condition)

    def remove_sql(self, model, schema_editor):
        condition = self._get_condition_sql(model, schema_editor)
        return schema_editor._delete_unique_sql(model, self.name, condition=condition)

    def __repr__(self):
        """
        Generate a string representation of the object.
        
        Args:
        self (object): The object instance.
        
        Returns:
        str: A string representation of the object.
        
        Summary:
        This function generates a string representation of the object using the class name, fields, name, and condition (if present). It uses the `__class__.__name__`, `fields`, `name`, and `condition` attributes of the object to create the string representation.
        """

        return '<%s: fields=%r name=%r%s>' % (
            self.__class__.__name__, self.fields, self.name,
            '' if self.condition is None else ' condition=%s' % self.condition,
        )

    def __eq__(self, other):
        """
        Compares two `UniqueConstraint` instances for equality.
        
        This method checks if the given `other` object is an instance of `UniqueConstraint` and compares its attributes: `name`, `fields`, and `condition`. Two `UniqueConstraint` instances are considered equal if all these attributes match.
        
        Args:
        other (UniqueConstraint): The `UniqueConstraint` instance to compare with.
        
        Returns:
        bool: True if the instances are equal, False otherwise.
        """

        return (
            isinstance(other, UniqueConstraint) and
            self.name == other.name and
            self.fields == other.fields and
            self.condition == other.condition
        )

    def deconstruct(self):
        """
        Deconstructs the current object into its constituent parts.
        
        This method is used to break down the object into its fundamental components, specifically the path, arguments, and keyword arguments. It also includes additional fields and conditions specific to this object type.
        
        Args:
        None (This method is called automatically when needed, such as during serialization or deserialization.)
        
        Returns:
        tuple: A tuple containing the path, arguments, and keyword arguments of the object. The keyword arguments include 'fields' and
        """

        path, args, kwargs = super().deconstruct()
        kwargs['fields'] = self.fields
        if self.condition:
            kwargs['condition'] = self.condition
        return path, args, kwargs
