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
        Tests the migration process for the 'migrations_ipaddressfield' model.
        
        This function ensures that the specified model's tables are correctly managed during the migration process. It first checks if the table does not exist, then runs a migration to create it, and finally verifies that the table is created. After that, it unmigrates everything to ensure that the table is removed.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Assert that the 'migrations_ipaddressfield'
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
