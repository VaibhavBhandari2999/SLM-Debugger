"""
```markdown
This Django management command tests the behavior of deprecated model fields in historical migrations. It ensures that fields marked as deprecated can still be used in past migration states.

#### Classes and Functions:
- **Tests**: A subclass of `MigrationTestBase` that contains tests for migrating models with deprecated fields.
  - **test_migrate**: A test method that verifies the correct creation and removal of a table (`migrations_ipaddressfield`) during the migration process.

#### Key Responsibilities:
- The `test_migrate` method checks if a table exists before and after running migration commands, ensuring that the table is correctly created and removed based on the migration commands.

#### Interactions:
- The `Tests` class uses `assertTableExists` and `
"""
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
        Tests the migration process for the 'migrations_ipaddressfield' model. Ensures that the table is not created initially, then creates it after running the migration command, and finally removes it by unmigrating everything. Verifies the existence of the table using assertTableExists and assertTableNotExists methods.
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
