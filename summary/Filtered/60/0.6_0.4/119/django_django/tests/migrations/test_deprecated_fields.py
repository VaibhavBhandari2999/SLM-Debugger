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
        
        This function ensures that the migration process works correctly for the 'migrations_ipaddressfield' model. It checks that the table does not exist before the migration, the table exists after the migration, and that the table is removed when unmigrating.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Steps:
        1. Asserts that the 'migrations_ipaddressfield' table does not exist.
        2. Runs the
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
