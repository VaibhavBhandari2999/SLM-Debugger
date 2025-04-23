from unittest import mock, skipUnless

from django.db import OperationalError, connection
from django.test import TestCase


@skipUnless(connection.vendor == 'sqlite', 'SQLite tests.')
class FeaturesTests(TestCase):
    def test_supports_json_field_operational_error(self):
        """
        Tests the behavior of the `supports_json_field` feature when an `OperationalError` is raised during database cursor operations.
        
        This function checks whether the database connection's `supports_json_field` feature is correctly handled when an `OperationalError` occurs while trying to open a database cursor. It involves the following steps:
        1. Checks if the `supports_json_field` feature is present in the connection's features.
        2. Temporarily removes the `supports_json_field` feature if it exists.
        3
        """

        if hasattr(connection.features, 'supports_json_field'):
            del connection.features.supports_json_field
        msg = 'unable to open database file'
        with mock.patch(
            'django.db.backends.base.base.BaseDatabaseWrapper.cursor',
            side_effect=OperationalError(msg),
        ):
            with self.assertRaisesMessage(OperationalError, msg):
                connection.features.supports_json_field
