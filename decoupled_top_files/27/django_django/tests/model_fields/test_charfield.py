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
        Tests the behavior of saving and retrieving a post with an emoji in its title.
        
        Args:
        None
        
        Returns:
        None
        
        Methods:
        - `Post.objects.create`: Creates a new post instance with the given title and body.
        - `refresh_from_db`: Refreshes the post instance from the database to ensure the latest data is used.
        - `assertEqual`: Compares the expected title with the actual title after saving and refreshing the post.
        
        Important Variables:
        """

        p = Post.objects.create(title='Smile 😀', body='Whatever.')
        p.refresh_from_db()
        self.assertEqual(p.title, 'Smile 😀')

    def test_assignment_from_choice_enum(self):
        """
        Tests assignment from choice enum.
        
        This function creates a `Post` object with `title` and `body` assigned
        values from an `Event` enum. It then verifies that the values are correctly
        set and retrieved, and checks if two posts with the same title are equal.
        
        Functions Used:
        - `models.TextChoices`: Defines a text-based choices field.
        - `Post.objects.create()`: Creates a new `Post` instance.
        - `refresh_from_db
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
        Tests that a CharField raises a ValidationError when an empty string is passed to its clean method.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the CharField's clean method does not raise an error when an empty string is passed.
        
        Functions Used:
        - models.CharField
        - self.assertRaises
        - f.clean
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
        Tests that a CharField with choices raises a ValidationError when an invalid choice is provided.
        
        Args:
        self: The instance of the test case class.
        
        Attributes:
        f (CharField): A CharField with defined choices.
        
        Raises:
        ValidationError: If an invalid choice ('not a') is passed to the clean method.
        """

        f = models.CharField(choices=[('a', 'A'), ('b', 'B')])
        with self.assertRaises(ValidationError):
            f.clean('not a', None)

    def test_enum_choices_cleans_valid_string(self):
        f = models.CharField(choices=self.Choices.choices, max_length=1)
        self.assertEqual(f.clean('c', None), 'c')

    def test_enum_choices_invalid_input(self):
        """
        Tests that invalid input raises a ValidationError when cleaning a CharField with choices.
        
        Args:
        self: The instance of the test class.
        
        Important Functions:
        - `models.CharField`: Defines a character field with specified choices and maximum length.
        - `clean`: Validates and cleans the input value.
        - `self.assertRaises`: Asserts that a specific exception is raised during the test.
        
        Input Variables:
        - 'a': The invalid input value passed to the clean method.
        """

        f = models.CharField(choices=self.Choices.choices, max_length=1)
        with self.assertRaises(ValidationError):
            f.clean('a', None)

    def test_charfield_raises_error_on_empty_input(self):
        """
        Tests that a CharField raises a ValidationError when given an empty input.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the CharField is given an empty input.
        
        Important Functions:
        - models.CharField: Defines the CharField with null set to False.
        - self.assertRaises: Context manager used to assert that a specific exception is raised.
        - f.clean: Cleans the input value and raises ValidationError if necessary.
        """

        f = models.CharField(null=False)
        with self.assertRaises(ValidationError):
            f.clean(None, None)
