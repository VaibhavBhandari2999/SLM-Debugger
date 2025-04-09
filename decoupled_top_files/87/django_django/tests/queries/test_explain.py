"""
The provided Python file contains unit tests for the `explain` method of Django's QuerySet. The `ExplainTests` class includes several test methods to verify the behavior of the `explain` method under different conditions, such as various query formats, options, and database-specific behaviors. The `ExplainUnsupportedTests` class provides a test case to ensure that the `explain` method is not called when the database backend does not support it. The tests cover a wide range of scenarios, including filtering, selecting related and prefetched related objects, annotating, ordering, unioning, and using specific options for PostgreSQL and MySQL databases. The tests also handle exceptions like `ValueError` and `NotSupportedError` appropriately. The file uses Django's
"""
import json
import unittest
import xml.etree.ElementTree

from django.db import NotSupportedError, connection, transaction
from django.db.models import Count
from django.test import TestCase, skipIfDBFeature, skipUnlessDBFeature
from django.test.utils import CaptureQueriesContext

from .models import Tag


@skipUnlessDBFeature('supports_explaining_query_execution')
class ExplainTests(TestCase):

    def test_basic(self):
        """
        Tests basic functionality of the QuerySet explain method.
        
        This function iterates over various QuerySets and formats, executing the `explain` method on each combination to ensure that the output is valid and formatted correctly. The important functions used include `filter`, `select_related`, `prefetch_related`, `annotate`, `values_list`, `order_by`, `union`, `select_for_update`, and `explain`. The supported formats for the `explain` method are checked against the database connection's features.
        """

        querysets = [
            Tag.objects.filter(name='test'),
            Tag.objects.filter(name='test').select_related('parent'),
            Tag.objects.filter(name='test').prefetch_related('children'),
            Tag.objects.filter(name='test').annotate(Count('children')),
            Tag.objects.filter(name='test').values_list('name'),
            Tag.objects.order_by().union(Tag.objects.order_by().filter(name='test')),
            Tag.objects.all().select_for_update().filter(name='test'),
        ]
        supported_formats = connection.features.supported_explain_formats
        all_formats = (None,) + tuple(supported_formats) + tuple(f.lower() for f in supported_formats)
        for idx, queryset in enumerate(querysets):
            for format in all_formats:
                with self.subTest(format=format, queryset=idx):
                    with self.assertNumQueries(1), CaptureQueriesContext(connection) as captured_queries:
                        result = queryset.explain(format=format)
                        self.assertTrue(captured_queries[0]['sql'].startswith(connection.ops.explain_prefix))
                        self.assertIsInstance(result, str)
                        self.assertTrue(result)
                        if format == 'xml':
                            try:
                                xml.etree.ElementTree.fromstring(result)
                            except xml.etree.ElementTree.ParseError as e:
                                self.fail(
                                    f'QuerySet.explain() result is not valid XML: {e}'
                                )
                        elif format == 'json':
                            try:
                                json.loads(result)
                            except json.JSONDecodeError as e:
                                self.fail(
                                    f'QuerySet.explain() result is not valid JSON: {e}'
                                )

    @skipUnlessDBFeature('validates_explain_options')
    def test_unknown_options(self):
        with self.assertRaisesMessage(ValueError, 'Unknown options: test, test2'):
            Tag.objects.all().explain(test=1, test2=1)

    def test_unknown_format(self):
        """
        Test that an unknown format raises a ValueError.
        
        This function checks if the provided format is supported by the database
        connection's features. If not, it raises a ValueError with a message
        indicating the unsupported format and the allowed formats (if any).
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If the provided format is not supported.
        
        Usage:
        This function can be used to validate the format parameter in queries
        that require an explain
        """

        msg = 'DOES NOT EXIST is not a recognized format.'
        if connection.features.supported_explain_formats:
            msg += ' Allowed formats: %s' % ', '.join(sorted(connection.features.supported_explain_formats))
        with self.assertRaisesMessage(ValueError, msg):
            Tag.objects.all().explain(format='does not exist')

    @unittest.skipUnless(connection.vendor == 'postgresql', 'PostgreSQL specific')
    def test_postgres_options(self):
        """
        Tests various PostgreSQL query options using the `explain` method on a queryset of tags.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `filter`: Filters the queryset based on the tag name.
        - `explain`: Generates an explanation of the query plan using specified options.
        - `transaction.atomic`: Ensures that the database transaction is managed properly.
        - `CaptureQueriesContext`: Captures the SQL queries generated during the transaction.
        
        Keywords:
        """

        qs = Tag.objects.filter(name='test')
        test_options = [
            {'COSTS': False, 'BUFFERS': True, 'ANALYZE': True},
            {'costs': False, 'buffers': True, 'analyze': True},
            {'verbose': True, 'timing': True, 'analyze': True},
            {'verbose': False, 'timing': False, 'analyze': True},
            {'summary': True},
        ]
        if connection.features.is_postgresql_12:
            test_options.append({'settings': True})
        if connection.features.is_postgresql_13:
            test_options.append({'analyze': True, 'wal': True})
        for options in test_options:
            with self.subTest(**options), transaction.atomic():
                with CaptureQueriesContext(connection) as captured_queries:
                    qs.explain(format='text', **options)
                self.assertEqual(len(captured_queries), 1)
                for name, value in options.items():
                    option = '{} {}'.format(name.upper(), 'true' if value else 'false')
                    self.assertIn(option, captured_queries[0]['sql'])

    @unittest.skipUnless(connection.vendor == 'mysql', 'MySQL specific')
    def test_mysql_text_to_traditional(self):
        """
        Tests the ability to generate an EXPLAIN query in TEXT format with TRADITIONAL output for a given filter on the 'name' field of the Tag model.
        
        This function ensures that the cached properties related to supported explain formats are initialized, captures the SQL queries generated by Django's ORM, and checks if the EXPLAIN query includes the 'FORMAT=TRADITIONAL' option.
        
        :param self: The instance of the test class.
        :type self: unittest.TestCase
        :return:
        """

        # Ensure these cached properties are initialized to prevent queries for
        # the MariaDB or MySQL version during the QuerySet evaluation.
        connection.features.supported_explain_formats
        with CaptureQueriesContext(connection) as captured_queries:
            Tag.objects.filter(name='test').explain(format='text')
        self.assertEqual(len(captured_queries), 1)
        self.assertIn('FORMAT=TRADITIONAL', captured_queries[0]['sql'])

    @unittest.skipUnless(connection.vendor == 'mysql', 'MariaDB and MySQL >= 8.0.18 specific.')
    def test_mysql_analyze(self):
        """
        Tests the MySQL analyze functionality for a queryset.
        
        This function filters tags with the name 'test' and uses the `explain` method
        with `analyze=True` to capture the SQL query executed by Django's ORM. It checks
        that the captured query starts with the appropriate prefix ('ANALYZE' or 'EXPLAIN ANALYZE')
        based on the database backend. Additionally, it tests the `explain` method with
        `analyze=True` and `format='JSON
        """

        qs = Tag.objects.filter(name='test')
        with CaptureQueriesContext(connection) as captured_queries:
            qs.explain(analyze=True)
        self.assertEqual(len(captured_queries), 1)
        prefix = 'ANALYZE ' if connection.mysql_is_mariadb else 'EXPLAIN ANALYZE '
        self.assertTrue(captured_queries[0]['sql'].startswith(prefix))
        with CaptureQueriesContext(connection) as captured_queries:
            qs.explain(analyze=True, format='JSON')
        self.assertEqual(len(captured_queries), 1)
        if connection.mysql_is_mariadb:
            self.assertIn('FORMAT=JSON', captured_queries[0]['sql'])
        else:
            self.assertNotIn('FORMAT=JSON', captured_queries[0]['sql'])


@skipIfDBFeature('supports_explaining_query_execution')
class ExplainUnsupportedTests(TestCase):

    def test_message(self):
        """
        Test that the `explain` method is not supported by the current backend.
        
        This function asserts that attempting to call the `explain` method on a
        filtered queryset of `Tag` objects will raise a `NotSupportedError` with
        the specific message: "This backend does not support explaining query
        execution."
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        NotSupportedError: If the `explain` method is called on the filtered
        queryset
        """

        msg = 'This backend does not support explaining query execution.'
        with self.assertRaisesMessage(NotSupportedError, msg):
            Tag.objects.filter(name='test').explain()
