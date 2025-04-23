from unittest import mock, skipUnless

from django.db import OperationalError, connection
from django.test import TestCase


@skipUnless(connection.vendor == 'sqlite', 'SQLite tests.')
class FeaturesTests(TestCase):
    def test_supports_json_field_operational_error(self):
        """
        Tests the behavior of the database connection when the 'supports_json_field' feature is disabled and an OperationalError is raised during a database operation.
        
        Key Parameters:
        - None
        
        Key Keywords:
        - None
        
        Inputs:
        - None
        
        Outputs:
        - Raises `OperationalError` with the message 'unable to open database file' if the 'supports_json_field' feature is not supported and an error occurs during the database operation.
        
        This function is designed to test how the database connection handles errors when the 'supports
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
