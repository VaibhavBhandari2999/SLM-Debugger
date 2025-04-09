"""
The provided Python file contains unit tests for the `Article` model's query set iterator functionality. It includes tests to validate the behavior of the `iterator` method under different conditions, such as invalid chunk sizes, default chunk sizes, and scenarios where chunked reads are not supported by the database backend.

#### Main Classes and Functions:
- **QuerySetIteratorTests**: A Django test case class that defines multiple test methods to validate the `iterator` method of the `Article` model's manager.
- **setUpTestData**: A class method that creates two instances of the `Article` model for testing purposes.
- **test_iterator_invalid_chunk_size**: Tests the behavior of the `iterator` method when an invalid chunk size is provided.
- **test_default
"""
import datetime
from unittest import mock

from django.db import connections
from django.db.models.sql.compiler import cursor_iter
from django.test import TestCase

from .models import Article


class QuerySetIteratorTests(TestCase):
    itersize_index_in_mock_args = 3

    @classmethod
    def setUpTestData(cls):
        Article.objects.create(name='Article 1', created=datetime.datetime.now())
        Article.objects.create(name='Article 2', created=datetime.datetime.now())

    def test_iterator_invalid_chunk_size(self):
        """
        Tests the behavior of the `iterator` method of the `Article` model's manager when an invalid chunk size is provided.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If the chunk size is not strictly positive.
        
        Important Functions:
        - `Article.objects.iterator(chunk_size=size)`: Generates an iterator for the `Article` model's objects with the specified chunk size.
        
        Keywords:
        - `Article.objects.iterator`
        - `chunk_size`
        """

        for size in (0, -1):
            with self.subTest(size=size):
                with self.assertRaisesMessage(ValueError, 'Chunk size must be strictly positive.'):
                    Article.objects.iterator(chunk_size=size)

    def test_default_iterator_chunk_size(self):
        """
        Tests the default iterator chunk size for a queryset of Article objects. It uses a mock patch to intercept the cursor iteration and verifies that the chunk size is set to 2000.
        """

        qs = Article.objects.iterator()
        with mock.patch('django.db.models.sql.compiler.cursor_iter', side_effect=cursor_iter) as cursor_iter_mock:
            next(qs)
        self.assertEqual(cursor_iter_mock.call_count, 1)
        mock_args, _mock_kwargs = cursor_iter_mock.call_args
        self.assertEqual(mock_args[self.itersize_index_in_mock_args], 2000)

    def test_iterator_chunk_size(self):
        """
        Tests the iterator chunk size for a queryset of Article objects. The function patches the cursor_iter method to simulate cursor iteration behavior. It sets the chunk size to 3 and iterates over the queryset using the iterator method. The test verifies that the cursor_iter method is called once with the specified chunk size.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `Article.objects.iterator`: Iterates over the queryset of Article objects with a specified chunk size.
        -
        """

        batch_size = 3
        qs = Article.objects.iterator(chunk_size=batch_size)
        with mock.patch('django.db.models.sql.compiler.cursor_iter', side_effect=cursor_iter) as cursor_iter_mock:
            next(qs)
        self.assertEqual(cursor_iter_mock.call_count, 1)
        mock_args, _mock_kwargs = cursor_iter_mock.call_args
        self.assertEqual(mock_args[self.itersize_index_in_mock_args], batch_size)

    def test_no_chunked_reads(self):
        """
        If the database backend doesn't support chunked reads, then the
        result of SQLCompiler.execute_sql() is a list.
        """
        qs = Article.objects.all()
        compiler = qs.query.get_compiler(using=qs.db)
        features = connections[qs.db].features
        with mock.patch.object(features, 'can_use_chunked_reads', False):
            result = compiler.execute_sql(chunked_fetch=True)
        self.assertIsInstance(result, list)
