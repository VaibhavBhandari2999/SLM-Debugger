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
        f = models.TextField(choices=[('A', 'A'), ('B', 'B')])
        self.assertIsInstance(f.formfield().widget, forms.Select)

    def test_to_python(self):
        """TextField.to_python() should return a string."""
        f = models.TextField()
        self.assertEqual(f.to_python(1), '1')

    def test_lookup_integer_in_textfield(self):
        self.assertEqual(Post.objects.filter(body=24).count(), 0)

    def test_emoji(self):
        """
        Tests the functionality of the emoji in a post's body.
        
        This function creates a new post with a title and a body containing an emoji.
        After creating the post, it refreshes the object from the database and checks
        if the body of the post contains the original emoji as expected.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - Creates a Post object with the title 'Whatever' and body 'Smile 😀.'
        - Refreshes the post object from the database.
        - Assert
        """

        p = Post.objects.create(title='Whatever', body='Smile 😀.')
        p.refresh_from_db()
        self.assertEqual(p.body, 'Smile 😀.')


class TestMethods(SimpleTestCase):
    def test_deconstruct(self):
        """
        Tests the deconstruct method of a TextField model.
        
        The deconstruct method is used to represent a model field as a tuple, suitable for serialization. This test function checks that the deconstruct method returns the correct parameters for a TextField model, both with and without custom settings.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        field (models.TextField): The TextField model instance to test.
        
        Key Keywords:
        db_collation (str): The database collation setting for the TextField.
        
        Expected
        """

        field = models.TextField()
        *_, kwargs = field.deconstruct()
        self.assertEqual(kwargs, {})
        field = models.TextField(db_collation='utf8_esperanto_ci')
        *_, kwargs = field.deconstruct()
        self.assertEqual(kwargs, {'db_collation': 'utf8_esperanto_ci'})
