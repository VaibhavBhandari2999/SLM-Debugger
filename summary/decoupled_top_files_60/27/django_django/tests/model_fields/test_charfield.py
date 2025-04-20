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
        Tests the behavior of the `title` field in the `Post` model when an emoji is used.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - Creates a new `Post` object with a title containing an emoji.
        - Refreshes the object from the database to ensure changes are saved.
        - Asserts that the `title` field of the `Post` object is correctly stored as 'Smile 😀'.
        """

        p = Post.objects.create(title='Smile 😀', body='Whatever.')
        p.refresh_from_db()
        self.assertEqual(p.title, 'Smile 😀')

    def test_assignment_from_choice_enum(self):
        """
        Tests the assignment of choices from an Enum to a model field.
        
        This function tests the assignment of choices from an Enum to a model field. It creates a model with a TextChoices field and assigns values to the field using the Enum. It then checks if the values are correctly assigned and retrieved from the database.
        
        Key Parameters:
        - None
        
        Key Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - The function does not return any value. It performs assertions to check the correctness of the assignment
        """

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
        """
        Test that a CharField raises a ValidationError when provided with an empty string.
        
        Args:
        f (CharField): The CharField instance to test.
        
        Raises:
        ValidationError: If the empty string is successfully validated by the CharField.
        
        Note:
        This test assumes that the CharField is configured to not allow empty strings.
        """

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
        
        Args:
        f (CharField): The CharField instance with defined choices.
        
        Raises:
        ValidationError: If the invalid choice ('not a') is passed to the clean method.
        
        Returns:
        None: The function does not return anything, it raises an exception if the invalid choice is not caught.
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
        Tests that a ValidationError is raised when a CharField with null=False is provided an empty input.
        
        Parameters:
        f (CharField): The CharField instance being tested, which is configured to not allow null values.
        
        Returns:
        None: The function does not return anything, but it is expected to raise a ValidationError if the input is empty.
        """

        f = models.CharField(null=False)
        with self.assertRaises(ValidationError):
            f.clean(None, None)
