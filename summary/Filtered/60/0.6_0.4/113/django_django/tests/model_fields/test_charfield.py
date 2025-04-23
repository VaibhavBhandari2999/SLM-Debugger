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
        p = Post.objects.create(title="Smile 😀", body="Whatever.")
        p.refresh_from_db()
        self.assertEqual(p.title, "Smile 😀")

    def test_assignment_from_choice_enum(self):
        """
        Tests the assignment of choices from an Enum-like model field.
        
        This function creates instances of the `Post` model with choices from the `Event` Enum-like model field. It then checks if the assignment and retrieval of these choices are correct.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - `Event`: A model field with choices defined as a TextChoices enum-like class.
        - `Post`: A model with `title` and `body` fields, both of type `Event
        """

        class Event(models.TextChoices):
            C = "Carnival!"
            F = "Festival!"

        p1 = Post.objects.create(title=Event.C, body=Event.F)
        p1.refresh_from_db()
        self.assertEqual(p1.title, "Carnival!")
        self.assertEqual(p1.body, "Festival!")
        self.assertEqual(p1.title, Event.C)
        self.assertEqual(p1.body, Event.F)
        p2 = Post.objects.get(title="Carnival!")
        self.assertEqual(p1, p2)
        self.assertEqual(p2.title, Event.C)


class TestMethods(SimpleTestCase):
    def test_deconstruct(self):
        field = models.CharField()
        *_, kwargs = field.deconstruct()
        self.assertEqual(kwargs, {})
        field = models.CharField(db_collation="utf8_esperanto_ci")
        *_, kwargs = field.deconstruct()
        self.assertEqual(kwargs, {"db_collation": "utf8_esperanto_ci"})


class ValidationTests(SimpleTestCase):
    class Choices(models.TextChoices):
        C = "c", "C"

    def test_charfield_raises_error_on_empty_string(self):
        f = models.CharField()
        msg = "This field cannot be blank."
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean("", None)

    def test_charfield_cleans_empty_string_when_blank_true(self):
        f = models.CharField(blank=True)
        self.assertEqual("", f.clean("", None))

    def test_charfield_with_choices_cleans_valid_choice(self):
        f = models.CharField(max_length=1, choices=[("a", "A"), ("b", "B")])
        self.assertEqual("a", f.clean("a", None))

    def test_charfield_with_choices_raises_error_on_invalid_choice(self):
        f = models.CharField(choices=[("a", "A"), ("b", "B")])
        msg = "Value 'not a' is not a valid choice."
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean("not a", None)

    def test_enum_choices_cleans_valid_string(self):
        f = models.CharField(choices=self.Choices.choices, max_length=1)
        self.assertEqual(f.clean("c", None), "c")

    def test_enum_choices_invalid_input(self):
        """
        Test the validation of an invalid input for a CharField with predefined choices.
        
        This function tests the validation mechanism for a CharField that has predefined choices. It ensures that an invalid input, which is not part of the defined choices, raises a ValidationError with a specific error message.
        
        Parameters:
        self (unittest.TestCase): The test case instance for running the test.
        
        Returns:
        None: This function does not return any value. It raises an assertion error if the test fails.
        
        Key Parameters:
        -
        """

        f = models.CharField(choices=self.Choices.choices, max_length=1)
        msg = "Value 'a' is not a valid choice."
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean("a", None)

    def test_charfield_raises_error_on_empty_input(self):
        """
        Test the CharField validation for empty input.
        
        This function tests whether a CharField with null set to False raises a ValidationError when provided with an empty input.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the CharField does not raise an error when provided with None as input.
        
        Key Points:
        - The CharField instance is created with null=False.
        - The clean method is called with None as input.
        - A specific error message is expected to be raised.
        """

        f = models.CharField(null=False)
        msg = "This field cannot be null."
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean(None, None)
