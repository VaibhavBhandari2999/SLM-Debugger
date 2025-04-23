from unittest import mock, skipUnless

from django.db import OperationalError, connection
from django.test import TestCase


@skipUnless(connection.vendor == 'sqlite', 'SQLite tests.')
class FeaturesTests(TestCase):
    def test_supports_json_field_operational_error(self):
        """
        Tests the behavior of the `supports_json_field` feature when an `OperationalError` is raised during database cursor operations.
        
        This function checks whether the `supports_json_field` feature of the database connection is correctly handled when an `OperationalError` occurs. It first attempts to delete the `supports_json_field` attribute from the `connection.features` object. Then, it uses a mock to simulate an `OperationalError` when trying to open a database cursor. If the `supports_json_field
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
