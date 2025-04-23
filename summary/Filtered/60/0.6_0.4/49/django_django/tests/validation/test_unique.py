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
        Test the unique fields collection in a Django model.
        
        This function checks the unique fields of a model and ensures that they are correctly identified and collected.
        
        Parameters:
        - m (UniqueFieldsModel): The model instance to test.
        
        Returns:
        - tuple: A tuple containing two lists. The first list contains tuples of the model and its unique fields. The second list is expected to be empty, indicating no additional unique checks are needed.
        
        Example:
        >>> m = UniqueFieldsModel()
        >>> test_unique_fields_get_col
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
        Tests the unique checks for a model excluding a specific field.
        
        This function checks the unique constraints for the `UniqueForDateModel` model, excluding the 'start_date' field. It returns a tuple containing two lists:
        1. The first list contains the unique checks for the model, with the primary key ('id') as the unique field.
        2. The second list contains additional unique checks for the model, based on 'year', 'count', and 'end_date', as well as 'month
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
        # Regression test for #12560
        with self.assertNumQueries(0):
            mtv = ModelToValidate(number=10, name='Some Name')
            setattr(mtv, '_adding', True)
            mtv.full_clean()

    def test_primary_key_unique_check_performed_when_adding_and_pk_specified(self):
        # Regression test for #12560
        with self.assertNumQueries(1):
            mtv = ModelToValidate(number=10, name='Some Name', id=123)
            setattr(mtv, '_adding', True)
            mtv.full_clean()

    def test_primary_key_unique_check_not_performed_when_not_adding(self):
        # Regression test for #12132
        with self.assertNumQueries(0):
            mtv = ModelToValidate(number=10, name='Some Name')
            mtv.full_clean()

    def test_unique_for_date(self):
        """
        Tests the uniqueness of fields based on the 'posted' date for a Post model.
        
        This function creates and validates Post objects to ensure that certain fields are unique for specific date parts:
        - 'title' must be unique for a given 'posted' date.
        - 'slug' must be unique for a given 'posted' year.
        - 'subtitle' must be unique for a given 'posted' month.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the validation fails
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
        UniqueErrorsModel.objects.create(name='Some Name', no=10)
        m = UniqueErrorsModel(name='Some Name', no=11)
        with self.assertRaises(ValidationError) as cm:
            m.full_clean()
        self.assertEqual(cm.exception.message_dict, {'name': ['Custom unique name message.']})

        m = UniqueErrorsModel(name='Some Other Name', no=10)
        with self.assertRaises(ValidationError) as cm:
            m.full_clean()
        self.assertEqual(cm.exception.message_dict, {'no': ['Custom unique number message.']})
empt to create a second instance with the same 'name' as the first instance, expecting a
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
