from django.core.management import call_command
from django.test import override_settings

from .test_base import MigrationTestBase


class Tests(MigrationTestBase):
    """
    Deprecated model fields should still be usable in historic migrations.
    """

    @override_settings(
        MIGRATION_MODULES={"migrations": "migrations.deprecated_field_migrations"}
    )
    def test_migrate(self):
        """
        Tests the migration process for the 'migrations_ipaddressfield' table.
        
        This function ensures that the specified table is correctly managed during the migration process. It first checks if the table does not exist, then runs a migration to create it, and finally checks that the table has been created. After that, it unmigrates everything to revert the changes and checks that the table is no longer present.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Asserts that the '
        """

        # Make sure no tables are created
        self.assertTableNotExists("migrations_ipaddressfield")
        # Run migration
        call_command("migrate", verbosity=0)
        # Make sure the right tables exist
        self.assertTableExists("migrations_ipaddressfield")
        # Unmigrate everything
        call_command("migrate", "migrations", "zero", verbosity=0)
        # Make sure it's all gone
        self.assertTableNotExists("migrations_ipaddressfield")
