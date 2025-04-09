"""
This Python file contains definitions for several classes and methods related to database and state operations in Django migrations. The key components are:

1. **SeparateDatabaseAndState**: This class separates operations into those that affect the database and those that affect the state. It allows for more granular control over how operations are applied during migrations.

2. **RunSQL**: This class is used to run raw SQL commands. It supports both forward and backward migrations and can optionally provide state operations to handle custom schema changes.

3. **RunPython**: This class runs Python code in a context suitable for performing versioned ORM operations. It supports both forward and backward migrations and can be used to perform complex operations that are difficult to express in SQL.

Each class includes methods
"""
from django.db import router

from .base import Operation


class SeparateDatabaseAndState(Operation):
    """
    Take two lists of operations - ones that will be used for the database,
    and ones that will be used for the state change. This allows operations
    that don't support state change to have it applied, or have operations
    that affect the state or not the database, or so on.
    """

    serialization_expand_args = ['database_operations', 'state_operations']

    def __init__(self, database_operations=None, state_operations=None):
        self.database_operations = database_operations or []
        self.state_operations = state_operations or []

    def deconstruct(self):
        """
        Deconstructs the object into its constituent parts.
        
        Args:
        None
        
        Returns:
        A tuple containing:
        - The class name (str): The qualified name of the class.
        - An empty list (list): An empty list representing the positional arguments.
        - A dictionary (dict): A dictionary containing the keyword arguments, which include:
        - database_operations (list): A list of database operations.
        - state_operations (list): A list of state operations.
        """

        kwargs = {}
        if self.database_operations:
            kwargs['database_operations'] = self.database_operations
        if self.state_operations:
            kwargs['state_operations'] = self.state_operations
        return (
            self.__class__.__qualname__,
            [],
            kwargs
        )

    def state_forwards(self, app_label, state):
        for state_operation in self.state_operations:
            state_operation.state_forwards(app_label, state)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """
        Generates database operations for a given app label and schema editor. It iterates through a list of database operations, updating the state of the application's database schema. For each operation, it creates a new state clone, applies the operation to this new state, and then executes the forward operation on the specified schema editor. The process is repeated until all operations are processed.
        
        Args:
        app_label (str): The label of the Django application whose database schema is being updated.
        schema_editor:
        """

        # We calculate state separately in here since our state functions aren't useful
        for database_operation in self.database_operations:
            to_state = from_state.clone()
            database_operation.state_forwards(app_label, to_state)
            database_operation.database_forwards(app_label, schema_editor, from_state, to_state)
            from_state = to_state

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        """
        Reverses the operations of a migration.
        
        Args:
        app_label (str): The label of the Django application containing the migration.
        schema_editor: An instance of the schema editor used to execute database operations.
        from_state: The current state of the database before applying the migration.
        to_state: The target state of the database after applying the migration.
        
        This method calculates the state of the database by applying each database operation in reverse order,
        using the `state_forwards`
        """

        # We calculate state separately in here since our state functions aren't useful
        to_states = {}
        for dbop in self.database_operations:
            to_states[dbop] = to_state
            to_state = to_state.clone()
            dbop.state_forwards(app_label, to_state)
        # to_state now has the states of all the database_operations applied
        # which is the from_state for the backwards migration of the last
        # operation.
        for database_operation in reversed(self.database_operations):
            from_state = to_state
            to_state = to_states[database_operation]
            database_operation.database_backwards(app_label, schema_editor, from_state, to_state)

    def describe(self):
        return "Custom state/database change combination"


class RunSQL(Operation):
    """
    Run some raw SQL. A reverse SQL statement may be provided.

    Also accept a list of operations that represent the state change effected
    by this SQL change, in case it's custom column/table creation/deletion.
    """
    noop = ''

    def __init__(self, sql, reverse_sql=None, state_operations=None, hints=None, elidable=False):
        """
        Initialize a new instance of the class.
        
        Args:
        sql (str): The SQL query to be executed.
        reverse_sql (str, optional): The SQL query to be executed in reverse. Defaults to None.
        state_operations (list, optional): A list of state operations to be performed. Defaults to an empty list.
        hints (dict, optional): A dictionary of hints to be used during execution. Defaults to an empty dictionary.
        elidable (bool, optional): Indicates whether
        """

        self.sql = sql
        self.reverse_sql = reverse_sql
        self.state_operations = state_operations or []
        self.hints = hints or {}
        self.elidable = elidable

    def deconstruct(self):
        """
        Deconstructs the current object into its constituent parts.
        
        Args:
        None
        
        Returns:
        A tuple containing:
        - The class name (str): The qualified name of the class.
        - An empty list (list): An empty list, indicating no positional arguments are required.
        - A dictionary (dict): A dictionary containing the following keys and their corresponding values:
        - 'sql' (str): The SQL query string.
        - 'reverse_sql' (str, optional
        """

        kwargs = {
            'sql': self.sql,
        }
        if self.reverse_sql is not None:
            kwargs['reverse_sql'] = self.reverse_sql
        if self.state_operations:
            kwargs['state_operations'] = self.state_operations
        if self.hints:
            kwargs['hints'] = self.hints
        return (
            self.__class__.__qualname__,
            [],
            kwargs
        )

    @property
    def reversible(self):
        return self.reverse_sql is not None

    def state_forwards(self, app_label, state):
        for state_operation in self.state_operations:
            state_operation.state_forwards(app_label, state)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        if router.allow_migrate(schema_editor.connection.alias, app_label, **self.hints):
            self._run_sql(schema_editor, self.sql)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        """
        Reverses a database migration operation.
        
        Args:
        app_label (str): The label of the Django application associated with the model being migrated.
        schema_editor: An instance of the schema editor used to execute SQL commands.
        from_state: The current state of the database before the migration.
        to_state: The target state of the database after the migration.
        
        Raises:
        NotImplementedError: If the `reverse_sql` attribute is not defined.
        
        Notes:
        - This method is called
        """

        if self.reverse_sql is None:
            raise NotImplementedError("You cannot reverse this operation")
        if router.allow_migrate(schema_editor.connection.alias, app_label, **self.hints):
            self._run_sql(schema_editor, self.reverse_sql)

    def describe(self):
        return "Raw SQL operation"

    def _run_sql(self, schema_editor, sqls):
        """
        Runs SQL commands using the provided schema editor.
        
        Args:
        schema_editor: The schema editor object used to execute the SQL commands.
        sqls: A list or tuple of SQL commands or a single SQL command string.
        
        Summary:
        This function takes a schema editor and a set of SQL commands (either a list/tuple or a single string) and executes them. It handles both lists/tuples of SQL commands with optional parameters and single SQL command strings. The function uses the `execute
        """

        if isinstance(sqls, (list, tuple)):
            for sql in sqls:
                params = None
                if isinstance(sql, (list, tuple)):
                    elements = len(sql)
                    if elements == 2:
                        sql, params = sql
                    else:
                        raise ValueError("Expected a 2-tuple but got %d" % elements)
                schema_editor.execute(sql, params=params)
        elif sqls != RunSQL.noop:
            statements = schema_editor.connection.ops.prepare_sql_script(sqls)
            for statement in statements:
                schema_editor.execute(statement, params=None)


class RunPython(Operation):
    """
    Run Python code in a context suitable for doing versioned ORM operations.
    """

    reduces_to_sql = False

    def __init__(self, code, reverse_code=None, atomic=None, hints=None, elidable=False):
        """
        This function is a RunPython operation that takes in a code and an optional reverse_code. It also has an optional atomic parameter, hints dictionary, and an elidable boolean. The code is a callable function that is used to modify the input variables. If reverse_code is provided, it is also a callable function that is used to revert the changes made by the code function. The hints dictionary provides additional information about the operation, and the elidable boolean indicates whether the operation can be removed without affecting the
        """

        self.atomic = atomic
        # Forwards code
        if not callable(code):
            raise ValueError("RunPython must be supplied with a callable")
        self.code = code
        # Reverse code
        if reverse_code is None:
            self.reverse_code = None
        else:
            if not callable(reverse_code):
                raise ValueError("RunPython must be supplied with callable arguments")
            self.reverse_code = reverse_code
        self.hints = hints or {}
        self.elidable = elidable

    def deconstruct(self):
        """
        Deconstructs the object into its constituent parts.
        
        Args:
        self: The object to be deconstructed.
        
        Returns:
        A tuple containing the class name, an empty list, and a dictionary of keyword arguments.
        
        Keyword Arguments:
        code (str): The code associated with the object.
        reverse_code (str, optional): The reverse code associated with the object.
        atomic (bool, optional): Whether the object is atomic or not.
        hints (list, optional): A
        """

        kwargs = {
            'code': self.code,
        }
        if self.reverse_code is not None:
            kwargs['reverse_code'] = self.reverse_code
        if self.atomic is not None:
            kwargs['atomic'] = self.atomic
        if self.hints:
            kwargs['hints'] = self.hints
        return (
            self.__class__.__qualname__,
            [],
            kwargs
        )

    @property
    def reversible(self):
        return self.reverse_code is not None

    def state_forwards(self, app_label, state):
        """
        Generates a state for the given app label. This method is intended to be overridden by subclasses to provide custom logic for generating the state. The default implementation does nothing.
        
        Args:
        app_label (str): The label of the Django application for which the state is being generated.
        
        Returns:
        None: By default, this method does not return any value. Subclasses should override this method to provide custom logic that returns a state object.
        """

        # RunPython objects have no state effect. To add some, combine this
        # with SeparateDatabaseAndState.
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """
        This function is responsible for executing database migrations for a specific app label. It first clears the delayed apps cache to ensure all models are up-to-date. Then, it checks if the given app label is allowed to migrate based on the provided router and hints. If migration is allowed, it executes the provided Python code within a context that includes the versioned models as an app registry. The function takes four parameters: app_label (str), schema_editor (object), from_state (State), and to_state
        """

        # RunPython has access to all models. Ensure that all models are
        # reloaded in case any are delayed.
        from_state.clear_delayed_apps_cache()
        if router.allow_migrate(schema_editor.connection.alias, app_label, **self.hints):
            # We now execute the Python code in a context that contains a 'models'
            # object, representing the versioned models as an app registry.
            # We could try to override the global cache, but then people will still
            # use direct imports, so we go with a documentation approach instead.
            self.code(from_state.apps, schema_editor)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        """
        Reverses the migration by executing the `reverse_code` method. This method is called when migrating backwards in the database.
        
        Args:
        app_label (str): The label of the application being migrated.
        schema_editor (SchemaEditor): The schema editor object used to execute database operations.
        from_state (ModelState): The current state of the model before the migration.
        to_state (ModelState): The target state of the model after the migration.
        
        Raises:
        NotImplementedError: If `reverse
        """

        if self.reverse_code is None:
            raise NotImplementedError("You cannot reverse this operation")
        if router.allow_migrate(schema_editor.connection.alias, app_label, **self.hints):
            self.reverse_code(from_state.apps, schema_editor)

    def describe(self):
        return "Raw Python operation"

    @staticmethod
    def noop(apps, schema_editor):
        return None
