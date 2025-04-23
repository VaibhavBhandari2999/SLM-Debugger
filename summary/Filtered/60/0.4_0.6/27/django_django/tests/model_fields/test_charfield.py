from unittest import skipIf

from django.core.exceptions import ValidationError
from django.db import connection, models
from django.test import SimpleTestCase, TestCase

from .models import Post


class TestCharField(TestCase):

    def test_max_length_passed_to_formfield(self):
        """
        CharField passes its max_length attribute to form fields created using
        the formfield() method.
        """
        cf1 = models.CharField()
        cf2 = models.CharField(max_length=1234)
        self.assertIsNone(cf1.formfield().max_length)
        self.assertEqual(1234, cf2.formfield().max_length)

    def test_lookup_integer_in_charfield(self):
        self.assertEqual(Post.objects.filter(title=9).count(), 0)

    @skipIf(connection.vendor == 'mysql', 'Running on MySQL requires utf8mb4 encoding (#18392)')
    def test_emoji(self):
        """
        Function: test_emoji
        Summary: Tests the behavior of the `title` field in the `Post` model when an emoji is used.
        Parameters:
        - self: The test case instance.
        Returns:
        None
        Key Points:
        - A new `Post` object is created with a title containing an emoji.
        - The `refresh_from_db` method is called to ensure the database is up-to-date.
        - The function asserts that the `title` field of the `
        """

        p = Post.objects.create(title='Smile 😀', body='Whatever.')
        p.refresh_from_db()
        self.assertEqual(p.title, 'Smile 😀')

    def test_assignment_from_choice_enum(self):
        class Event(models.TextChoices):
            C = 'Carnival!'
            F = 'Festival!'

        p1 = Post.objects.create(title=Event.C, body=Event.F)
        p1.refresh_from_db()
        self.assertEqual(p1.title, 'Carnival!')
        self.assertEqual(p1.body, 'Festival!')
        self.assertEqual(p1.title, Event.C)
        self.assertEqual(p1.body, Event.F)
        p2 = Post.objects.get(title='Carnival!')
        self.assertEqual(p1, p2)
        self.assertEqual(p2.title, Event.C)


class ValidationTests(SimpleTestCase):

    class Choices(models.TextChoices):
        C = 'c', 'C'

    def test_charfield_raises_error_on_empty_string(self):
        f = models.CharField()
        with self.assertRaises(ValidationError):
            f.clean('', None)

    def test_charfield_cleans_empty_string_when_blank_true(self):
        f = models.CharField(blank=True)
        self.assertEqual('', f.clean('', None))

    def test_charfield_with_choices_cleans_valid_choice(self):
        f = models.CharField(max_length=1, choices=[('a', 'A'), ('b', 'B')])
        self.assertEqual('a', f.clean('a', None))

    def test_charfield_with_choices_raises_error_on_invalid_choice(self):
        """
        Test that a CharField with choices raises a ValidationError for an invalid choice.
        
        Parameters:
        f (models.CharField): A CharField instance with choices defined.
        
        This function creates an instance of CharField with specified choices and then attempts to clean an invalid choice. It asserts that a ValidationError is raised when an invalid choice ('not a') is passed to the clean method.
        
        Returns:
        None: The function does not return anything, but it will raise an AssertionError if the validation does not occur as expected.
        """

        f = models.CharField(choices=[('a', 'A'), ('b', 'B')])
        with self.assertRaises(ValidationError):
            f.clean('not a', None)

    def test_enum_choices_cleans_valid_string(self):
        f = models.CharField(choices=self.Choices.choices, max_length=1)
        self.assertEqual(f.clean('c', None), 'c')

    def test_enum_choices_invalid_input(self):
        f = models.CharField(choices=self.Choices.choices, max_length=1)
        with self.assertRaises(ValidationError):
            f.clean('a', None)

    def test_charfield_raises_error_on_empty_input(self):
        """
        Tests that a ValidationError is raised when a CharField with null=False is provided with None as input.
        
        Parameters:
        f (CharField): A Django CharField instance configured with null=False.
        
        Returns:
        None: The function does not return anything, but raises a ValidationError if the input is invalid.
        
        Raises:
        ValidationError: If the input is None and the CharField is configured with null=False, this error is raised.
        """

        f = models.CharField(null=False)
        with self.assertRaises(ValidationError):
            f.clean(None, None)
