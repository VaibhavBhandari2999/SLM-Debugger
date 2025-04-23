import json
import uuid

from django.core.serializers.json import DjangoJSONEncoder
from django.forms import (
    CharField, Form, JSONField, Textarea, TextInput, ValidationError,
)
from django.test import SimpleTestCase


class JSONFieldTest(SimpleTestCase):
    def test_valid(self):
        field = JSONField()
        value = field.clean('{"a": "b"}')
        self.assertEqual(value, {'a': 'b'})

    def test_valid_empty(self):
        field = JSONField(required=False)
        self.assertIsNone(field.clean(''))
        self.assertIsNone(field.clean(None))

    def test_invalid(self):
        """
        Tests the validation of an invalid JSON input.
        
        This function tests the validation mechanism of a JSONField by attempting to clean an invalid JSON string. It raises a ValidationError with a specific error message if the input is not a valid JSON.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the input JSON string is not valid, an error message 'Enter a valid JSON.' is raised.
        
        Example Usage:
        >>> test_invalid()
        ValidationError: Enter a valid JSON.
        """

        field = JSONField()
        with self.assertRaisesMessage(ValidationError, 'Enter a valid JSON.'):
            field.clean('{some badly formed: json}')

    def test_prepare_value(self):
        field = JSONField()
        self.assertEqual(field.prepare_value({'a': 'b'}), '{"a": "b"}')
        self.assertEqual(field.prepare_value(None), 'null')
        self.assertEqual(field.prepare_value('foo'), '"foo"')
        self.assertEqual(field.prepare_value('你好，世界'), '"你好，世界"')
        self.assertEqual(field.prepare_value({'a': '😀🐱'}), '{"a": "😀🐱"}')
        self.assertEqual(
            field.prepare_value(["你好，世界", "jaźń"]),
            '["你好，世界", "jaźń"]',
        )

    def test_widget(self):
        field = JSONField()
        self.assertIsInstance(field.widget, Textarea)

    def test_custom_widget_kwarg(self):
        field = JSONField(widget=TextInput)
        self.assertIsInstance(field.widget, TextInput)

    def test_custom_widget_attribute(self):
        """The widget can be overridden with an attribute."""
        class CustomJSONField(JSONField):
            widget = TextInput

        field = CustomJSONField()
        self.assertIsInstance(field.widget, TextInput)

    def test_converted_value(self):
        """
        Tests the conversion of various JSON strings to their appropriate Python data types.
        
        This function tests the `clean` method of the `JSONField` class by converting different JSON strings to their corresponding Python data types. The `clean` method is expected to handle various types of JSON inputs and return the appropriate Python data types.
        
        Parameters:
        None
        
        Input:
        - `json_string` (str): A JSON string to be converted to a Python data type.
        
        Output:
        - `val` (any
        """

        field = JSONField(required=False)
        tests = [
            '["a", "b", "c"]',
            '{"a": 1, "b": 2}',
            '1',
            '1.5',
            '"foo"',
            'true',
            'false',
            'null',
        ]
        for json_string in tests:
            with self.subTest(json_string=json_string):
                val = field.clean(json_string)
                self.assertEqual(field.clean(val), val)

    def test_has_changed(self):
        field = JSONField()
        self.assertIs(field.has_changed({'a': True}, '{"a": 1}'), True)
        self.assertIs(field.has_changed({'a': 1, 'b': 2}, '{"b": 2, "a": 1}'), False)

    def test_custom_encoder_decoder(self):
        class CustomDecoder(json.JSONDecoder):
            def __init__(self, object_hook=None, *args, **kwargs):
                return super().__init__(object_hook=self.as_uuid, *args, **kwargs)

            def as_uuid(self, dct):
                if 'uuid' in dct:
                    dct['uuid'] = uuid.UUID(dct['uuid'])
                return dct

        value = {'uuid': uuid.UUID('{c141e152-6550-4172-a784-05448d98204b}')}
        encoded_value = '{"uuid": "c141e152-6550-4172-a784-05448d98204b"}'
        field = JSONField(encoder=DjangoJSONEncoder, decoder=CustomDecoder)
        self.assertEqual(field.prepare_value(value), encoded_value)
        self.assertEqual(field.clean(encoded_value), value)

    def test_formfield_disabled(self):
        """
        Tests the behavior of a disabled JSONField in a form.
        
        This function creates a form with a disabled JSONField and checks if the initial value is correctly displayed in the form output, despite the field being disabled.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Elements:
        - JSONForm: A form containing a single JSONField with the `disabled=True` attribute.
        - form: An instance of the JSONForm with initial data and submitted data.
        - assertIn: Verifies that
        """

        class JSONForm(Form):
            json_field = JSONField(disabled=True)

        form = JSONForm({'json_field': '["bar"]'}, initial={'json_field': ['foo']})
        self.assertIn('[&quot;foo&quot;]</textarea>', form.as_p())

    def test_redisplay_wrong_input(self):
        """
        Displaying a bound form (typically due to invalid input). The form
        should not overquote JSONField inputs.
        """
        class JSONForm(Form):
            name = CharField(max_length=2)
            json_field = JSONField()

        # JSONField input is valid, name is too long.
        form = JSONForm({'name': 'xyz', 'json_field': '["foo"]'})
        self.assertNotIn('json_field', form.errors)
        self.assertIn('[&quot;foo&quot;]</textarea>', form.as_p())
        # Invalid JSONField.
        form = JSONForm({'name': 'xy', 'json_field': '{"foo"}'})
        self.assertEqual(form.errors['json_field'], ['Enter a valid JSON.'])
        self.assertIn('{&quot;foo&quot;}</textarea>', form.as_p())
