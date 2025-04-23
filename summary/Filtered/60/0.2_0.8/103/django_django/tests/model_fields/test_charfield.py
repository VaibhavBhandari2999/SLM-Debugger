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
        Tests the assignment of values from a choice enum to a model field.
        
        This function creates a model with a `TextChoices` enum field and assigns values to it. It then checks if the values are correctly assigned and retrieved, and if querying the database with the assigned value returns the correct instance.
        
        Key Parameters:
        - None
        
        Key Return Values:
        - None
        
        Steps:
        1. Define a `Event` enum with two choices: 'Carnival!' and 'Festival!'.
        2. Create
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
        """
        Tests the deconstruction of a CharField.
        
        This function tests the deconstruction of a CharField model. It verifies that the deconstructed field does not have any additional keyword arguments by default, and that it correctly retains specified keyword arguments such as 'db_collation'.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        field (CharField): The CharField instance to be deconstructed.
        
        Key Keywords:
        db_collation (str): The database collation to be set on the
        """

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
        f = models.CharField(choices=self.Choices.choices, max_length=1)
        msg = "Value 'a' is not a valid choice."
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean("a", None)

    def test_charfield_raises_error_on_empty_input(self):
        f = models.CharField(null=False)
        msg = "This field cannot be null."
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean(None, None)
