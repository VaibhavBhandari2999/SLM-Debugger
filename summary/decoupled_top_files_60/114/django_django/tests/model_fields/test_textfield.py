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
        """
        Tests the functionality of saving an emoji in a Post object.
        
        This function creates a new Post object with a title and a body containing an emoji. After saving and refreshing the object from the database, it checks if the body still contains the emoji.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - A Post object is created with a title and a body containing an emoji.
        - The Post object is saved and refreshed from the database.
        - The function asserts that the body of the Post
        """

        p = Post.objects.create(title="Whatever", body="Smile 😀.")
        p.refresh_from_db()
        self.assertEqual(p.body, "Smile 😀.")


class TestMethods(SimpleTestCase):
    def test_deconstruct(self):
        field = models.TextField()
        *_, kwargs = field.deconstruct()
        self.assertEqual(kwargs, {})
        field = models.TextField(db_collation="utf8_esperanto_ci")
        *_, kwargs = field.deconstruct()
        self.assertEqual(kwargs, {"db_collation": "utf8_esperanto_ci"})
Equal(kwargs, {"db_collation": "utf8_esperanto_ci"})
