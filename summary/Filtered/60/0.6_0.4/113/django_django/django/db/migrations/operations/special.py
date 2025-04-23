from django.db import router

from .base import Operation


class SeparateDatabaseAndState(Operation):
    """
    Take two lists of operations - ones that will be used for the database,
    and ones that will be used for the state change. This allows operations
    that don't support state change to have it applied, or have operations
    that affect the state or not the database, or so on.
    """

    serialization_expand_args = ["database_operations", "state_operations"]

    def __init__(self, database_operations=None, state_operations=None):
        self.database_operations = database_operations or []
        self.state_operations = state_operations or []

    def deconstruct(self):
        """
        Deconstructs the current object into its component parts.
        
        This method breaks down the object into its fundamental components, specifically the database operations and state operations, and returns them as a tuple.
        
        Args:
        None
        
        Returns:
        tuple: A tuple containing the class name as a string, an empty list, and a dictionary of keyword arguments. The dictionary includes 'database_operations' and 'state_operations' if they are not empty.
        
        Example:
        >>> obj = SomeObject(database_operations=[...], state
        """

        kwargs = {}
        if self.database_operations:
            kwargs["database_operations"] = self.database_operations
        if self.state_operations:
            kwargs["state_operations"] = self.state_operations
        return (self.__class__.__qualname__, [], kwargs)

    def state_forwards(self, app_label, state):
        for state_operation in self.state_operations:
            state_operation.state_forwards(app_label, state)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        # We calculate state separately in here since our state functions aren't useful
        for database_operation in self.database_operations:
            to_state = from_state.clone()
            database_operation.state_forwards(app_label, to_state)
            database_operation.database_forwards(
                app_label, schema_editor, from_state, to_state
            )
            from_state = to_state

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
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
            database_operation.database_backwards(
                app_label, schema_editor, from_state, to_state
            )

    def describe(self):
        return "Custom state/database change combination"


class RunSQL(Operation):
    """
    Run some raw SQL. A reverse SQL statement may be provided.

    Also accept a list of operations that represent the state change effected
    by this SQL change, in case it's custom column/table creation/deletion.
    """

    noop = ""

    def __init__(
        self, sql, reverse_sql=None, state_operations=None, hints=None, elidable=False
    ):
        self.sql = sql
        self.reverse_sql = reverse_sql
        self.state_operations = state_operations or []
        self.hints = hints or {}
        self.elidable = elidable

    def deconstruct(self):
        kwargs = {
            "sql": self.sql,
        }
        if self.reverse_sql is not None:
            kwargs["reverse_sql"] = self.reverse_sql
        if self.state_operations:
            kwargs["state_operations"] = self.state_operations
        if self.hints:
            kwargs["hints"] = self.hints
        return (self.__class__.__qualname__, [], kwargs)

    @property
    def reversible(self):
        return self.reverse_sql is not None

    def state_forwards(self, app_label, state):
        for state_operation in self.state_operations:
            state_operation.state_forwards(app_label, state)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        if router.allow_migrate(
            schema_editor.connection.alias, app_label, **self.hints
        ):
            self._run_sql(schema_editor, self.sql)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        """
        Generates SQL to reverse a database operation.
        
        This function is used to generate the SQL necessary to reverse a database operation. It checks if the reverse SQL is provided and if the migration is allowed for the given app label and connection alias. If both conditions are met, it executes the reverse SQL using the provided schema editor.
        
        Parameters:
        app_label (str): The label of the Django app for which the migration is being run.
        schema_editor: The schema editor used to execute SQL commands.
        """

        if self.reverse_sql is None:
            raise NotImplementedError("You cannot reverse this operation")
        if router.allow_migrate(
            schema_editor.connection.alias, app_label, **self.hints
        ):
            self._run_sql(schema_editor, self.reverse_sql)

    def describe(self):
        return "Raw SQL operation"

    def _run_sql(self, schema_editor, sqls):
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

    def __init__(
        self, code, reverse_code=None, atomic=None, hints=None, elidable=False
    ):
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
        kwargs = {
            "code": self.code,
        }
        if self.reverse_code is not None:
            kwargs["reverse_code"] = self.reverse_code
        if self.atomic is not None:
            kwargs["atomic"] = self.atomic
        if self.hints:
            kwargs["hints"] = self.hints
        return (self.__class__.__qualname__, [], kwargs)

    @property
    def reversible(self):
        return self.reverse_code is not None

    def state_forwards(self, app_label, state):
        """
        Function to handle the state transition for a given app label.
        
        This function is designed to be overridden or extended to provide specific state transitions for a Django app label. By default, it does nothing as it is intended to be combined with `SeparateDatabaseAndState` to add state effects.
        
        Parameters:
        app_label (str): The label of the Django app for which the state transition is being handled.
        
        Returns:
        None: This function does not return any value by default. It is meant to
        """

        # RunPython objects have no state effect. To add some, combine this
        # with SeparateDatabaseAndState.
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        # RunPython has access to all models. Ensure that all models are
        # reloaded in case any are delayed.
        from_state.clear_delayed_apps_cache()
        if router.allow_migrate(
            schema_editor.connection.alias, app_label, **self.hints
        ):
            # We now execute the Python code in a context that contains a 'models'
            # object, representing the versioned models as an app registry.
            # We could try to override the global cache, but then people will still
            # use direct imports, so we go with a documentation approach instead.
            self.code(from_state.apps, schema_editor)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        """
        Generates a database migration operation that runs in reverse.
        
        This function is used to create a migration that reverses the effects of a previous migration. It is called during the migration process to apply the reverse operation.
        
        Parameters:
        app_label (str): The label of the Django app that contains the model being migrated.
        schema_editor (object): An instance of the schema editor used to execute database operations.
        from_state (ModelState): The current state of the models before the migration.
        to_state
        """

        if self.reverse_code is None:
            raise NotImplementedError("You cannot reverse this operation")
        if router.allow_migrate(
            schema_editor.connection.alias, app_label, **self.hints
        ):
            self.reverse_code(from_state.apps, schema_editor)

    def describe(self):
        return "Raw Python operation"

    @staticmethod
    def noop(apps, schema_editor):
        return None
