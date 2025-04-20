from unittest import mock, skipUnless

from django.db import OperationalError, connection
from django.test import TestCase


@skipUnless(connection.vendor == 'sqlite', 'SQLite tests.')
class FeaturesTests(TestCase):
    def test_supports_json_field_operational_error(self):
        """
        Tests the behavior of the `supports_json_field` feature when the database connection encounters an `OperationalError`.
        
        This function checks whether the `supports_json_field` feature of the database connection is correctly handled when an `OperationalError` is raised. The `supports_json_field` attribute is first checked to see if it exists. If it does, it is temporarily deleted to simulate a scenario where the feature status is unknown. The function then patches the `cursor` method of the database connection to raise
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
