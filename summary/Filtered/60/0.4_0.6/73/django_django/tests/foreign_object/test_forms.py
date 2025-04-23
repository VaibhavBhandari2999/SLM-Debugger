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
        
        This function tests the form validation and saving process for an ArticleForm that includes a foreign object field. The form is instantiated and validated with different data points to ensure that the non-concrete fields (like 'active_translation') are not included in the form fields. It also checks that the form can correctly save and update an instance of the Article model.
        
        Parameters:
        - form: An instance of ArticleForm used for testing.
        
        Key Steps:
        1
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
