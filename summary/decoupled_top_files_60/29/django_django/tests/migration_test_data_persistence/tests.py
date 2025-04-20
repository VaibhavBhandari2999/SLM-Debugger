from django.test import TestCase, TransactionTestCase

from .models import Book


class MigrationDataPersistenceTestCase(TransactionTestCase):
    """
    Data loaded in migrations is available if
    TransactionTestCase.serialized_rollback = True.
    """

    available_apps = ["migration_test_data_persistence"]
    serialized_rollback = True

    def test_persistence(self):
        self.assertEqual(
            Book.objects.count(),
            1,
        )


class MigrationDataNormalPersistenceTestCase(TestCase):
    """
    Data loaded in migrations is available on TestCase
    """

    def test_persistence(self):
        """
        Tests the persistence of a Book object in the database.
        
        This function checks if a Book object has been successfully persisted in the database by verifying its count. No parameters are required for this test.
        
        Key Parameters:
        - None
        
        Returns:
        - None
        """

        self.assertEqual(
            Book.objects.count(),
            1,
        )
