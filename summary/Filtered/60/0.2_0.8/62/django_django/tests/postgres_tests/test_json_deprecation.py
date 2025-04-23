try:
    from django.contrib.postgres import forms
    from django.contrib.postgres.fields import JSONField
    from django.contrib.postgres.fields.jsonb import (
        KeyTextTransform, KeyTransform,
    )
except ImportError:
    pass

from django.core.checks import Warning as DjangoWarning
from django.utils.deprecation import RemovedInDjango40Warning

from . import PostgreSQLSimpleTestCase
from .models import PostgreSQLModel


class DeprecationTests(PostgreSQLSimpleTestCase):
    def test_model_field_deprecation_message(self):
        """
        Tests the deprecation message for the JSONField in PostgreSQLModel.
        
        This function checks that the correct deprecation warning is raised when using
        the JSONField from django.contrib.postgres.fields in a PostgreSQLModel. The
        warning should indicate that the field is deprecated and suggest using
        django.db.models.JSONField instead.
        
        Parameters:
        None
        
        Returns:
        list: A list of DjangoWarning objects indicating the deprecation message.
        """

        class PostgreSQLJSONModel(PostgreSQLModel):
            field = JSONField()

        self.assertEqual(PostgreSQLJSONModel().check(), [
            DjangoWarning(
                'django.contrib.postgres.fields.JSONField is deprecated. '
                'Support for it (except in historical migrations) will be '
                'removed in Django 4.0.',
                hint='Use django.db.models.JSONField instead.',
                obj=PostgreSQLJSONModel._meta.get_field('field'),
                id='fields.W904',
            ),
        ])

    def test_form_field_deprecation_message(self):
        msg = (
            'django.contrib.postgres.forms.JSONField is deprecated in favor '
            'of django.forms.JSONField.'
        )
        with self.assertWarnsMessage(RemovedInDjango40Warning, msg):
            forms.JSONField()

    def test_key_transform_deprecation_message(self):
        msg = (
            'django.contrib.postgres.fields.jsonb.KeyTransform is deprecated '
            'in favor of django.db.models.fields.json.KeyTransform.'
        )
        with self.assertWarnsMessage(RemovedInDjango40Warning, msg):
            KeyTransform('foo', 'bar')

    def test_key_text_transform_deprecation_message(self):
        """
        Tests the deprecation message for KeyTextTransform in the context of Django's PostgreSQL fields.
        
        This function asserts that a specific deprecation warning is raised when using the KeyTextTransform class from django.contrib.postgres.fields.jsonb. The warning message indicates that the class is deprecated and suggests using django.db.models.fields.json.KeyTextTransform instead.
        
        Key Parameters:
        - None
        
        Returns:
        - None
        
        Raises:
        - RemovedInDjango40Warning: A deprecation warning is expected to be raised.
        
        Usage
        """

        msg = (
            'django.contrib.postgres.fields.jsonb.KeyTextTransform is '
            'deprecated in favor of '
            'django.db.models.fields.json.KeyTextTransform.'
        )
        with self.assertWarnsMessage(RemovedInDjango40Warning, msg):
            KeyTextTransform('foo', 'bar')
