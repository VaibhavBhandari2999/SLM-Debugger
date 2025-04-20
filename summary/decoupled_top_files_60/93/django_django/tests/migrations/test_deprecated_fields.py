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
        
        This function verifies that the migration process works as expected for the 'migrations_ipaddressfield' model. It ensures that the table is not created initially, then runs the migration to create it, and finally un-migrates to ensure the table is removed.
        
        Key Parameters:
        - None
        
        Keywords:
        - None
        
        Inputs:
        - None
        
        Outputs:
        - None
        
        Steps:
        1. Assert that the 'migrations_ipaddress
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
