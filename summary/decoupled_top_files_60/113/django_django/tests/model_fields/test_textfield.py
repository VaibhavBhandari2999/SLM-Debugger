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
        
        This function checks the deconstruction of a TextField model instance. It verifies that the deconstructed fields do not contain any keyword arguments when no specific options are provided. When a specific option, such as 'db_collation', is provided, it ensures that the keyword argument is correctly included in the deconstructed fields.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - field: An instance of the TextField model.
        
        Key Keywords:
        -
        """

        field = models.TextField()
        *_, kwargs = field.deconstruct()
        self.assertEqual(kwargs, {})
        field = models.TextField(db_collation="utf8_esperanto_ci")
        *_, kwargs = field.deconstruct()
        self.assertEqual(kwargs, {"db_collation": "utf8_esperanto_ci"})
