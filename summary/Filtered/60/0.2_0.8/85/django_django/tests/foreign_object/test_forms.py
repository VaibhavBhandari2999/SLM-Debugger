import datetime

from django import forms
from django.test import TestCase

from .models import Article


class FormsTests(TestCase):
    # ForeignObjects should not have any form fields, currently the user needs
    # to manually deal with the foreignobject relation.
    class ArticleForm(forms.ModelForm):
        class Meta:
            model = Article
            fields = '__all__'

    def test_foreign_object_form(self):
        """
        Test the behavior of a form with a foreign object field.
        
        This test checks that the form correctly handles a non-concrete field, ensuring that it does not generate form fields for it. The form is validated and saved multiple times to ensure that the non-concrete field is properly handled.
        
        Key Parameters:
        - form: The form instance to test.
        
        Key Steps:
        1. Verify that the form does not include the non-concrete field 'active_translation' in its table representation.
        2. Validate and save
        """

        # A very crude test checking that the non-concrete fields do not get form fields.
        form = FormsTests.ArticleForm()
        self.assertIn('id_pub_date', form.as_table())
        self.assertNotIn('active_translation', form.as_table())
        form = FormsTests.ArticleForm(data={'pub_date': str(datetime.date.today())})
        self.assertTrue(form.is_valid())
        a = form.save()
        self.assertEqual(a.pub_date, datetime.date.today())
        form = FormsTests.ArticleForm(instance=a, data={'pub_date': '2013-01-01'})
        a2 = form.save()
        self.assertEqual(a.pk, a2.pk)
        self.assertEqual(a2.pub_date, datetime.date(2013, 1, 1))
