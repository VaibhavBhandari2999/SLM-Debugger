from django.contrib.postgres.signals import (
    get_citext_oids,
    get_hstore_oids,
    register_type_handlers,
)
from django.db import NotSupportedError, router
from django.db.migrations import AddConstraint, AddIndex, RemoveIndex
from django.db.migrations.operations.base import Operation
from django.db.models.constraints import CheckConstraint


class CreateExtension(Operation):
    reversible = True

    def __init__(self, name):
        self.name = name

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        if schema_editor.connection.vendor != "postgresql" or not router.allow_migrate(
            schema_editor.connection.alias, app_label
        ):
            return
        if not self.extension_exists(schema_editor, self.name):
            schema_editor.execute(
                "CREATE EXTENSION IF NOT EXISTS %s"
                % schema_editor.quote_name(self.name)
            )
        # Clear cached, stale oids.
        get_hstore_oids.cache_clear()
        get_citext_oids.cache_clear()
        # Registering new type handlers cannot be done before the extension is
        # installed, otherwise a subsequent data migration would use the same
        # connection.
        register_type_handlers(schema_editor.connection)
        if hasattr(schema_editor.connection, "register_geometry_adapters"):
            schema_editor.connection.register_geometry_adapters(
                schema_editor.connection.connection, True
            )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        """
        Drops an extension from the database.
        
        This method is used to drop an extension from the database during a migration process. It checks if the current database connection allows migration for the specified app label. If the extension exists, it is dropped. Additionally, it clears the cache for oids related to hstore and citext extensions.
        
        Parameters:
        app_label (str): The label of the Django application associated with the extension.
        schema_editor: An instance of the schema editor used to execute SQL commands
        """

        if not router.allow_migrate(schema_editor.connection.alias, app_label):
            return
        if self.extension_exists(schema_editor, self.name):
            schema_editor.execute(
                "DROP EXTENSION IF EXISTS %s" % schema_editor.quote_name(self.name)
            )
        # Clear cached, stale oids.
        get_hstore_oids.cache_clear()
        get_citext_oids.cache_clear()

    def extension_exists(self, schema_editor, extension):
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_extension WHERE extname = %s",
                [extension],
            )
            return bool(cursor.fetchone())

    def describe(self):
        return "Creates extension %s" % self.name

    @property
    def migration_name_fragment(self):
        return "create_extension_%s" % self.name


class BloomExtension(CreateExtension):
    def __init__(self):
        self.name = "bloom"


class BtreeGinExtension(CreateExtension):
    def __init__(self):
        self.name = "btree_gin"


class BtreeGistExtension(CreateExtension):
    def __init__(self):
        self.name = "btree_gist"


class CITextExtension(CreateExtension):
    def __init__(self):
        self.name = "citext"


class CryptoExtension(CreateExtension):
    def __init__(self):
        self.name = "pgcrypto"


class HStoreExtension(CreateExtension):
    def __init__(self):
        self.name = "hstore"


class TrigramExtension(CreateExtension):
    def __init__(self):
        self.name = "pg_trgm"


class UnaccentExtension(CreateExtension):
    def __init__(self):
        self.name = "unaccent"


class NotInTransactionMixin:
    def _ensure_not_in_transaction(self, schema_editor):
        if schema_editor.connection.in_atomic_block:
            raise NotSupportedError(
                "The %s operation cannot be executed inside a transaction "
                "(set atomic = False on the migration)." % self.__class__.__name__
            )


class AddIndexConcurrently(NotInTransactionMixin, AddIndex):
    """Create an index using PostgreSQL's CREATE INDEX CONCURRENTLY syntax."""

    atomic = False

    def describe(self):
        """
        Generates a description of the index creation process for a given model.
        
        This function returns a string that describes the process of concurrently creating an index on specified fields of a model.
        
        Parameters:
        self (object): The instance of the class containing the index and model information.
        
        Returns:
        str: A formatted string describing the index creation process.
        
        Example:
        >>> describe()
        'Concurrently create index my_index on field(s) name, age of model User'
        """

        return "Concurrently create index %s on field(s) %s of model %s" % (
            self.index.name,
            ", ".join(self.index.fields),
            self.model_name,
        )

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        self._ensure_not_in_transaction(schema_editor)
        model = to_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, model):
            schema_editor.add_index(model, self.index, concurrently=True)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        """
        Remove an index from a model in the database.
        
        This function is used to remove an index from a specific model in the database. It is typically called during a migration process.
        
        Parameters:
        app_label (str): The label of the application containing the model.
        schema_editor (SchemaEditor): The schema editor object used to perform the database operations.
        from_state (ModelState): The current state of the model before the migration.
        to_state (ModelState): The target state of the model after the
        """

        self._ensure_not_in_transaction(schema_editor)
        model = from_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, model):
            schema_editor.remove_index(model, self.index, concurrently=True)


class RemoveIndexConcurrently(NotInTransactionMixin, RemoveIndex):
    """Remove an index using PostgreSQL's DROP INDEX CONCURRENTLY syntax."""

    atomic = False

    def describe(self):
        return "Concurrently remove index %s from %s" % (self.name, self.model_name)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        self._ensure_not_in_transaction(schema_editor)
        model = from_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, model):
            from_model_state = from_state.models[app_label, self.model_name_lower]
            index = from_model_state.get_index_by_name(self.name)
            schema_editor.remove_index(model, index, concurrently=True)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        self._ensure_not_in_transaction(schema_editor)
        model = to_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, model):
            to_model_state = to_state.models[app_label, self.model_name_lower]
            index = to_model_state.get_index_by_name(self.name)
            schema_editor.add_index(model, index, concurrently=True)


class CollationOperation(Operation):
    def __init__(self, name, locale, *, provider="libc", deterministic=True):
        """
        Initialize a new instance of the class.
        
        Args:
        name (str): The name of the locale.
        locale (str): The locale to be used.
        provider (str, optional): The provider to use for the locale. Defaults to "libc".
        deterministic (bool, optional): Whether to use deterministic behavior. Defaults to True.
        
        Returns:
        None: This function does not return any value.
        """

        self.name = name
        self.locale = locale
        self.provider = provider
        self.deterministic = deterministic

    def state_forwards(self, app_label, state):
        pass

    def deconstruct(self):
        kwargs = {"name": self.name, "locale": self.locale}
        if self.provider and self.provider != "libc":
            kwargs["provider"] = self.provider
        if self.deterministic is False:
            kwargs["deterministic"] = self.deterministic
        return (
            self.__class__.__qualname__,
            [],
            kwargs,
        )

    def create_collation(self, schema_editor):
        args = {"locale": schema_editor.quote_name(self.locale)}
        if self.provider != "libc":
            args["provider"] = schema_editor.quote_name(self.provider)
        if self.deterministic is False:
            args["deterministic"] = "false"
        schema_editor.execute(
            "CREATE COLLATION %(name)s (%(args)s)"
            % {
                "name": schema_editor.quote_name(self.name),
                "args": ", ".join(
                    f"{option}={value}" for option, value in args.items()
                ),
            }
        )

    def remove_collation(self, schema_editor):
        schema_editor.execute(
            "DROP COLLATION %s" % schema_editor.quote_name(self.name),
        )


class CreateCollation(CollationOperation):
    """Create a collation."""

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        if schema_editor.connection.vendor != "postgresql" or not router.allow_migrate(
            schema_editor.connection.alias, app_label
        ):
            return
        self.create_collation(schema_editor)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        if not router.allow_migrate(schema_editor.connection.alias, app_label):
            return
        self.remove_collation(schema_editor)

    def describe(self):
        return f"Create collation {self.name}"

    @property
    def migration_name_fragment(self):
        return "create_collation_%s" % self.name.lower()


class RemoveCollation(CollationOperation):
    """Remove a collation."""

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """
        Method to handle database migrations for PostgreSQL.
        
        This method is designed to be used as part of a database migration process, specifically for PostgreSQL databases. It ensures that certain database operations are only performed if the current database connection is a PostgreSQL database and if the application is allowed to migrate.
        
        Parameters:
        app_label (str): The label of the Django application being migrated.
        schema_editor (SchemaEditor): The schema editor object used to perform database operations.
        from_state (ModelState): The current state of the
        """

        if schema_editor.connection.vendor != "postgresql" or not router.allow_migrate(
            schema_editor.connection.alias, app_label
        ):
            return
        self.remove_collation(schema_editor)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        if not router.allow_migrate(schema_editor.connection.alias, app_label):
            return
        self.create_collation(schema_editor)

    def describe(self):
        return f"Remove collation {self.name}"

    @property
    def migration_name_fragment(self):
        return "remove_collation_%s" % self.name.lower()


class AddConstraintNotValid(AddConstraint):
    """
    Add a table constraint without enforcing validation, using PostgreSQL's
    NOT VALID syntax.
    """

    def __init__(self, model_name, constraint):
        if not isinstance(constraint, CheckConstraint):
            raise TypeError(
                "AddConstraintNotValid.constraint must be a check constraint."
            )
        super().__init__(model_name, constraint)

    def describe(self):
        return "Create not valid constraint %s on model %s" % (
            self.constraint.name,
            self.model_name,
        )

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model = from_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, model):
            constraint_sql = self.constraint.create_sql(model, schema_editor)
            if constraint_sql:
                # Constraint.create_sql returns interpolated SQL which makes
                # params=None a necessity to avoid escaping attempts on
                # execution.
                schema_editor.execute(str(constraint_sql) + " NOT VALID", params=None)

    @property
    def migration_name_fragment(self):
        return super().migration_name_fragment + "_not_valid"


class ValidateConstraint(Operation):
    """Validate a table NOT VALID constraint."""

    def __init__(self, model_name, name):
        self.model_name = model_name
        self.name = name

    def describe(self):
        return "Validate constraint %s on model %s" % (self.name, self.model_name)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model = from_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, model):
            schema_editor.execute(
                "ALTER TABLE %s VALIDATE CONSTRAINT %s"
                % (
                    schema_editor.quote_name(model._meta.db_table),
                    schema_editor.quote_name(self.name),
                )
            )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        # PostgreSQL does not provide a way to make a constraint invalid.
        pass

    def state_forwards(self, app_label, state):
        pass

    @property
    def migration_name_fragment(self):
        return "%s_validate_%s" % (self.model_name.lower(), self.name.lower())

    def deconstruct(self):
        """
        Deconstructs the object into a tuple containing the class name, a list of positional arguments (which is empty in this case), and a dictionary of keyword arguments.
        
        Args:
        self (object): The instance of the class to be deconstructed.
        
        Returns:
        tuple: A tuple with three elements:
        - str: The class name of the object.
        - list: An empty list of positional arguments.
        - dict: A dictionary containing the keyword arguments 'model_name' and
        """

        return (
            self.__class__.__name__,
            [],
            {
                "model_name": self.model_name,
                "name": self.name,
            },
        )
