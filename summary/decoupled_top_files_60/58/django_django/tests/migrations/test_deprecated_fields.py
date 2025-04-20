from django.core.management import call_command
from django.test import override_settings

from .test_base import MigrationTestBase


class Tests(MigrationTestBase):
    """
    Deprecated model fields should still be usable in historic migrations.
    """
    @override_settings(MIGRATION_MODULES={"migrations": "migrations.deprecated_field_migrations"})
    def test_migrate(self):
        """
        Tests the migration process for the 'migrations_ipaddressfield' table.
        
        This function ensures that the specified table is correctly created and then removed through the migration process.
        
        Key Parameters:
        - None
        
        Keywords:
        - verbosity: Controls the amount of output during the migration process. Set to 0 for no output.
        
        Inputs:
        - None
        
        Outputs:
        - Assertions are made to check the existence of the 'migrations_ipaddressfield' table before and after the migration process.
        - The function uses the `
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
