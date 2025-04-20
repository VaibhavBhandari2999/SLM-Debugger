from django.core.exceptions import ValidationError
from django.db import models
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

    def test_emoji(self):
        """
        Tests the behavior of the `title` field in the `Post` model when it contains an emoji.
        
        This function creates a new `Post` object with a title that includes an emoji and then refreshes the object from the database. It asserts that the `title` field of the `Post` object matches the expected value after the refresh.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - A `Post` object is created with the title 'Smile 😀' and a
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


class TestMethods(SimpleTestCase):
    def test_deconstruct(self):
        """
        Tests the deconstruct method of a CharField.
        
        The deconstruct method is expected to return a tuple containing the field name and a dictionary of keyword arguments. The method is tested for two scenarios:
        1. A CharField without any additional parameters.
        2. A CharField with a specified 'db_collation' parameter.
        
        For the first scenario, the deconstruct method should return an empty dictionary for the keyword arguments.
        For the second scenario, the deconstruct method should return a dictionary with the 'db
        """

        field = models.CharField()
        *_, kwargs = field.deconstruct()
        self.assertEqual(kwargs, {})
        field = models.CharField(db_collation='utf8_esperanto_ci')
        *_, kwargs = field.deconstruct()
        self.assertEqual(kwargs, {'db_collation': 'utf8_esperanto_ci'})


class ValidationTests(SimpleTestCase):

    class Choices(models.TextChoices):
        C = 'c', 'C'

    def test_charfield_raises_error_on_empty_string(self):
        f = models.CharField()
        msg = 'This field cannot be blank.'
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('', None)

    def test_charfield_cleans_empty_string_when_blank_true(self):
        f = models.CharField(blank=True)
        self.assertEqual('', f.clean('', None))

    def test_charfield_with_choices_cleans_valid_choice(self):
        f = models.CharField(max_length=1, choices=[('a', 'A'), ('b', 'B')])
        self.assertEqual('a', f.clean('a', None))

    def test_charfield_with_choices_raises_error_on_invalid_choice(self):
        f = models.CharField(choices=[('a', 'A'), ('b', 'B')])
        msg = "Value 'not a' is not a valid choice."
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('not a', None)

    def test_enum_choices_cleans_valid_string(self):
        f = models.CharField(choices=self.Choices.choices, max_length=1)
        self.assertEqual(f.clean('c', None), 'c')

    def test_enum_choices_invalid_input(self):
        """
        Test the validation of an invalid input for a CharField with predefined choices.
        
        This function tests the validation mechanism for a CharField that is restricted to a set of choices. It ensures that an invalid choice raises a ValidationError with a specific error message.
        
        Parameters:
        self (unittest.TestCase): The test case instance for running the test.
        
        Returns:
        None: This function does not return any value. It raises an exception if the validation fails as expected.
        
        Key Parameters:
        - f (CharField):
        """

        f = models.CharField(choices=self.Choices.choices, max_length=1)
        msg = "Value 'a' is not a valid choice."
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('a', None)

    def test_charfield_raises_error_on_empty_input(self):
        f = models.CharField(null=False)
        msg = 'This field cannot be null.'
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean(None, None)
