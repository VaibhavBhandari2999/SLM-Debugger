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
        """
        Tests the persistence of a Book object in the database.
        
        This function checks if a Book object has been successfully saved and persisted in the database.
        
        Parameters:
        None
        
        Returns:
        None
        """

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
        Test the persistence of a book object in the database.
        
        This function checks if the count of book objects in the database is exactly 1.
        
        Parameters:
        None
        
        Returns:
        None
        """

        self.assertEqual(
            Book.objects.count(),
            1,
        )
