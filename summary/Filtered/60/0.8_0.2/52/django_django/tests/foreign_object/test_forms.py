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
        Test the form for the Article model.
        
        This test function checks the behavior of the form for the Article model. It ensures that the non-concrete fields do not generate form fields and validates the form's ability to handle date input and save instances correctly. The function performs the following steps:
        
        1. Creates an instance of the ArticleForm and checks that the 'pub_date' field is included in the form.
        2. Ensures that the 'active_translation' field is not included in the form.
        3
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
