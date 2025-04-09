import datetime
import unittest

from django.apps.registry import Apps
from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from .models import (
    CustomPKModel, FlexibleDatePost, ModelToValidate, Post, UniqueErrorsModel,
    UniqueFieldsModel, UniqueForDateModel, UniqueTogetherModel,
)


class GetUniqueCheckTests(unittest.TestCase):
    def test_unique_fields_get_collected(self):
        """
        Tests the `_get_unique_checks` method of `UniqueFieldsModel`. This method returns a list of unique fields for the model, specifically for 'id', 'unique_charfield', and 'unique_integerfield'. The expected output is a tuple containing a list of unique checks and an empty list.
        """

        m = UniqueFieldsModel()
        self.assertEqual(
            ([(UniqueFieldsModel, ('id',)),
              (UniqueFieldsModel, ('unique_charfield',)),
              (UniqueFieldsModel, ('unique_integerfield',))],
             []),
            m._get_unique_checks()
        )

    def test_unique_together_gets_picked_up_and_converted_to_tuple(self):
        """
        Tests that unique together constraints are correctly picked up and converted to tuples. The function compares the unique checks obtained from the model `UniqueTogetherModel` with expected values, expecting a list of unique checks involving fields 'ifield', 'cfield', 'efield', and 'id'. The function returns a tuple containing the unique checks and an empty list.
        """

        m = UniqueTogetherModel()
        self.assertEqual(
            ([(UniqueTogetherModel, ('ifield', 'cfield')),
              (UniqueTogetherModel, ('ifield', 'efield')),
              (UniqueTogetherModel, ('id',))],
             []),
            m._get_unique_checks()
        )

    def test_unique_together_normalization(self):
        """
        Test the Meta.unique_together normalization with different sorts of
        objects.
        """
        data = {
            '2-tuple': (('foo', 'bar'), (('foo', 'bar'),)),
            'list': (['foo', 'bar'], (('foo', 'bar'),)),
            'already normalized': ((('foo', 'bar'), ('bar', 'baz')),
                                   (('foo', 'bar'), ('bar', 'baz'))),
            'set': ({('foo', 'bar'), ('bar', 'baz')},  # Ref #21469
                    (('foo', 'bar'), ('bar', 'baz'))),
        }

        for unique_together, normalized in data.values():
            class M(models.Model):
                foo = models.IntegerField()
                bar = models.IntegerField()
                baz = models.IntegerField()

                Meta = type('Meta', (), {
                    'unique_together': unique_together,
                    'apps': Apps()
                })

            checks, _ = M()._get_unique_checks()
            for t in normalized:
                check = (M, t)
                self.assertIn(check, checks)

    def test_primary_key_is_considered_unique(self):
        m = CustomPKModel()
        self.assertEqual(([(CustomPKModel, ('my_pk_field',))], []), m._get_unique_checks())

    def test_unique_for_date_gets_picked_up(self):
        """
        Tests the `_get_unique_checks` method of the `UniqueForDateModel` class. This method returns a tuple containing unique checks for the model, including fields like 'id', 'date', 'count', 'start_date', 'year', 'month', and 'end_date'. The method is expected to return a specific tuple with two elements: a list of unique checks based on the primary key and a list of additional unique checks based on date-related fields and their transformations.
        """

        m = UniqueForDateModel()
        self.assertEqual((
            [(UniqueForDateModel, ('id',))],
            [(UniqueForDateModel, 'date', 'count', 'start_date'),
             (UniqueForDateModel, 'year', 'count', 'end_date'),
             (UniqueForDateModel, 'month', 'order', 'end_date')]
        ), m._get_unique_checks()
        )

    def test_unique_for_date_exclusion(self):
        """
        Generates unique checks for a model instance based on date fields.
        
        This function returns a tuple containing two lists: the first list
        specifies the unique constraints for the model, and the second list
        specifies additional unique checks excluding the 'start_date' field.
        
        Args:
        exclude (str): The field name to exclude from the unique checks.
        
        Returns:
        tuple: A tuple containing two lists. The first list contains the
        unique constraints for the model, and the second
        """

        m = UniqueForDateModel()
        self.assertEqual((
            [(UniqueForDateModel, ('id',))],
            [(UniqueForDateModel, 'year', 'count', 'end_date'),
             (UniqueForDateModel, 'month', 'order', 'end_date')]
        ), m._get_unique_checks(exclude='start_date')
        )


class PerformUniqueChecksTest(TestCase):
    def test_primary_key_unique_check_not_performed_when_adding_and_pk_not_specified(self):
        """
        Test that the primary key unique check is not performed when adding a new instance without specifying the primary key.
        
        This regression test ensures that the primary key unique check is skipped when creating a new instance of `ModelToValidate` without explicitly setting its primary key. The test uses `assertNumQueries` to verify that no database queries are executed during the validation process.
        
        Args:
        None
        
        Returns:
        None
        
        Methods/Functions Used:
        - `ModelToValidate`: The model
        """

        # Regression test for #12560
        with self.assertNumQueries(0):
            mtv = ModelToValidate(number=10, name='Some Name')
            setattr(mtv, '_adding', True)
            mtv.full_clean()

    def test_primary_key_unique_check_performed_when_adding_and_pk_specified(self):
        """
        Test that the primary key unique check is performed when adding a model instance with a specified primary key.
        
        This function ensures that the primary key uniqueness constraint is checked during the validation process of a model instance being added. It uses `assertNumQueries` to verify that only one database query is executed, indicating that the unique constraint check is performed efficiently.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the number of queries does not match the expected value or
        """

        # Regression test for #12560
        with self.assertNumQueries(1):
            mtv = ModelToValidate(number=10, name='Some Name', id=123)
            setattr(mtv, '_adding', True)
            mtv.full_clean()

    def test_primary_key_unique_check_not_performed_when_not_adding(self):
        """
        Tests that the primary key unique check is not performed when the instance is not being added to the database.
        
        This function ensures that the primary key uniqueness validation is skipped during model validation if the instance is not being created or updated in the database. It uses `assertNumQueries` to verify that no database queries are executed during the validation process.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If any database queries are executed during the validation process.
        
        Example
        """

        # Regression test for #12132
        with self.assertNumQueries(0):
            mtv = ModelToValidate(number=10, name='Some Name')
            mtv.full_clean()

    def test_unique_for_date(self):
        """
        Tests the unique validation constraints for the Post model based on different fields and their interactions with the 'posted' date.
        
        This function creates instances of the Post model with various combinations of fields and checks if they pass or fail the unique validation constraints based on the 'posted' date. The constraints are:
        - Title must be unique for the same posted date.
        - Slug must be unique for the same posted year.
        - Subtitle must be unique for the same posted month.
        - The
        """

        Post.objects.create(
            title="Django 1.0 is released", slug="Django 1.0",
            subtitle="Finally", posted=datetime.date(2008, 9, 3),
        )
        p = Post(title="Django 1.0 is released", posted=datetime.date(2008, 9, 3))
        with self.assertRaises(ValidationError) as cm:
            p.full_clean()
        self.assertEqual(cm.exception.message_dict, {'title': ['Title must be unique for Posted date.']})

        # Should work without errors
        p = Post(title="Work on Django 1.1 begins", posted=datetime.date(2008, 9, 3))
        p.full_clean()

        # Should work without errors
        p = Post(title="Django 1.0 is released", posted=datetime.datetime(2008, 9, 4))
        p.full_clean()

        p = Post(slug="Django 1.0", posted=datetime.datetime(2008, 1, 1))
        with self.assertRaises(ValidationError) as cm:
            p.full_clean()
        self.assertEqual(cm.exception.message_dict, {'slug': ['Slug must be unique for Posted year.']})

        p = Post(subtitle="Finally", posted=datetime.datetime(2008, 9, 30))
        with self.assertRaises(ValidationError) as cm:
            p.full_clean()
        self.assertEqual(cm.exception.message_dict, {'subtitle': ['Subtitle must be unique for Posted month.']})

        p = Post(title="Django 1.0 is released")
        with self.assertRaises(ValidationError) as cm:
            p.full_clean()
        self.assertEqual(cm.exception.message_dict, {'posted': ['This field cannot be null.']})

    def test_unique_for_date_with_nullable_date(self):
        """
        unique_for_date/year/month checks shouldn't trigger when the
        associated DateField is None.
        """
        FlexibleDatePost.objects.create(
            title="Django 1.0 is released", slug="Django 1.0",
            subtitle="Finally", posted=datetime.date(2008, 9, 3),
        )
        p = FlexibleDatePost(title="Django 1.0 is released")
        p.full_clean()

        p = FlexibleDatePost(slug="Django 1.0")
        p.full_clean()

        p = FlexibleDatePost(subtitle="Finally")
        p.full_clean()

    def test_unique_errors(self):
        """
        Test the validation errors raised by the UniqueErrorsModel.
        
        This test checks that the model raises the correct validation errors when
        attempting to create duplicate entries based on the 'name' and 'no'
        fields. The `full_clean` method is used to validate the model instance,
        and specific error messages are expected for each field.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the validation errors do not match the expected
        messages.
        """

        UniqueErrorsModel.objects.create(name='Some Name', no=10)
        m = UniqueErrorsModel(name='Some Name', no=11)
        with self.assertRaises(ValidationError) as cm:
            m.full_clean()
        self.assertEqual(cm.exception.message_dict, {'name': ['Custom unique name message.']})

        m = UniqueErrorsModel(name='Some Other Name', no=10)
        with self.assertRaises(ValidationError) as cm:
            m.full_clean()
        self.assertEqual(cm.exception.message_dict, {'no': ['Custom unique number message.']})
