from django.contrib.postgres.signals import (
    get_citext_oids, get_hstore_oids, register_type_handlers,
)
from django.db.migrations.operations.base import Operation


class CreateExtension(Operation):
    reversible = True

    def __init__(self, name):
        self.name = name

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """
        Creates an extension in the PostgreSQL database if it does not already exist. This function is specific to PostgreSQL and performs the following tasks:
        - Executes a SQL command to create an extension if it is not already present.
        - Clears the cache of old object identifiers (oids) for the hstore and citext extensions.
        - Registers new type handlers for the extension, ensuring that subsequent operations use the correct handlers.
        
        Parameters:
        - app_label (str): The label of the Django app containing the migration.
        - schema
        """

        if schema_editor.connection.vendor != 'postgresql':
            return
        schema_editor.execute("CREATE EXTENSION IF NOT EXISTS %s" % schema_editor.quote_name(self.name))
        # Clear cached, stale oids.
        get_hstore_oids.cache_clear()
        get_citext_oids.cache_clear()
        # Registering new type handlers cannot be done before the extension is
        # installed, otherwise a subsequent data migration would use the same
        # connection.
        register_type_handlers(schema_editor.connection)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        """
        Drops the specified extension from the database.
        
        This method is used to remove an extension from the database schema during a migration. It takes care of executing the necessary SQL command to drop the extension and clears the cached object identifiers (oids) for the hstore and citext extensions to ensure that the system does not retain stale information.
        
        Parameters:
        app_label (str): The label of the Django app associated with the migration.
        schema_editor (SchemaEditor): The schema editor object used to execute the
        """

        schema_editor.execute("DROP EXTENSION %s" % schema_editor.quote_name(self.name))
        # Clear cached, stale oids.
        get_hstore_oids.cache_clear()
        get_citext_oids.cache_clear()

    def describe(self):
        return "Creates extension %s" % self.name


class BtreeGinExtension(CreateExtension):

    def __init__(self):
        self.name = 'btree_gin'


class BtreeGistExtension(CreateExtension):

    def __init__(self):
        self.name = 'btree_gist'


class CITextExtension(CreateExtension):

    def __init__(self):
        self.name = 'citext'


class CryptoExtension(CreateExtension):

    def __init__(self):
        self.name = 'pgcrypto'


class HStoreExtension(CreateExtension):

    def __init__(self):
        self.name = 'hstore'


class TrigramExtension(CreateExtension):

    def __init__(self):
        self.name = 'pg_trgm'


class UnaccentExtension(CreateExtension):

    def __init__(self):
        self.name = 'unaccent'
