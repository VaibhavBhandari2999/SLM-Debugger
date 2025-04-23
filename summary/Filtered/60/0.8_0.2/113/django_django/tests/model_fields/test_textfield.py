from django import forms
from django.db import models
from django.test import SimpleTestCase, TestCase

from .models import Post


class TextFieldTests(TestCase):
    def test_max_length_passed_to_formfield(self):
        """
        TextField passes its max_length attribute to form fields created using
        their formfield() method.
        """
        tf1 = models.TextField()
        tf2 = models.TextField(max_length=2345)
        self.assertIsNone(tf1.formfield().max_length)
        self.assertEqual(2345, tf2.formfield().max_length)

    def test_choices_generates_select_widget(self):
        """A TextField with choices uses a Select widget."""
        f = models.TextField(choices=[("A", "A"), ("B", "B")])
        self.assertIsInstance(f.formfield().widget, forms.Select)

    def test_to_python(self):
        """TextField.to_python() should return a string."""
        f = models.TextField()
        self.assertEqual(f.to_python(1), "1")

    def test_lookup_integer_in_textfield(self):
        self.assertEqual(Post.objects.filter(body=24).count(), 0)

    def test_emoji(self):
        p = Post.objects.create(title="Whatever", body="Smile 😀.")
        p.refresh_from_db()
        self.assertEqual(p.body, "Smile 😀.")


class TestMethods(SimpleTestCase):
    def test_deconstruct(self):
        """
        Tests the deconstruction of a TextField model.
        
        This function tests the deconstruction of a TextField model instance. It verifies that the deconstructed fields are as expected, with and without specified database collation.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - field: An instance of the TextField model.
        
        Key Keywords:
        - db_collation: A string specifying the database collation for the TextField.
        
        Expected Outputs:
        - For a default TextField instance, the deconstructed kwargs should
        """

        field = models.TextField()
        *_, kwargs = field.deconstruct()
        self.assertEqual(kwargs, {})
        field = models.TextField(db_collation="utf8_esperanto_ci")
        *_, kwargs = field.deconstruct()
        self.assertEqual(kwargs, {"db_collation": "utf8_esperanto_ci"})
