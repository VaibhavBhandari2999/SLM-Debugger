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
        Tests the migration process for a custom model field.
        
        This function ensures that the migration process for a custom model field works as expected. It first checks that no tables are created for the specified model field. Then, it runs the migration to create the necessary tables. After that, it verifies that the tables exist. Finally, it unmigrates everything and checks that the tables are gone.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Assert that the table "migrations_ip
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
