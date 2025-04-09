"""
This Python file contains unit tests for a `JSONField` class, which is designed to handle JSON data in Django forms and models. The tests cover various aspects of the `JSONField`, including:

- Validation of JSON strings (`test_valid`, `test_valid_empty`, `test_invalid`)
- Conversion of Python data types to JSON strings and vice versa (`test_prepare_value`, `test_converted_value`)
- Widget handling (`test_widget`, `test_custom_widget_kwarg`, `test_custom_widget_attribute`)
- Comparison of old and new values (`test_has_changed`)
- Custom JSON encoder and decoder support (`test_custom_encoder_decoder`)
- Behavior in forms (`test_formfield_disabled`, `test_redisplay_wrong_input`)

The `JSONField` class
"""
import json
import uuid

from django.core.serializers.json import DjangoJSONEncoder
from django.forms import (
    CharField, Form, JSONField, Textarea, TextInput, ValidationError,
)
from django.test import SimpleTestCase


class JSONFieldTest(SimpleTestCase):
    def test_valid(self):
        """
        Tests the validation of a JSONField with a valid JSON string input. The JSONField's clean method is called with the string '{"a": "b"}', which is then expected to be returned as a dictionary {'a': 'b'}.
        """

        field = JSONField()
        value = field.clean('{"a": "b"}')
        self.assertEqual(value, {'a': 'b'})

    def test_valid_empty(self):
        """
        Tests the validation of an empty string or None value for a JSONField.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `JSONField`: A field that validates and stores JSON data.
        - `clean`: Validates and cleans the input data.
        
        Input Variables:
        - `field`: An instance of JSONField with `required=False`.
        
        Output Variables:
        - None (validates and returns None for empty string and None inputs).
        """

        field = JSONField(required=False)
        self.assertIsNone(field.clean(''))
        self.assertIsNone(field.clean(None))

    def test_invalid(self):
        """
        Tests the validation of an invalid JSON string using the JSONField's clean method.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        ValidationError: If the input JSON string is not valid.
        
        Important Functions:
        - JSONField.clean: Validates the input JSON string.
        
        Input Variables:
        - '{some badly formed: json}' (str): An invalid JSON string.
        
        Output Variables:
        - None
        """

        field = JSONField()
        with self.assertRaisesMessage(ValidationError, 'Enter a valid JSON.'):
            field.clean('{some badly formed: json}')

    def test_prepare_value(self):
        """
        Prepare a value for storage in the database.
        
        This method converts various types of input into their corresponding
        JSON-formatted string representations. It handles dictionaries, `None`,
        strings, and lists containing Unicode characters or emojis.
        
        Args:
        value (dict, str, list, None): The input value to be prepared.
        
        Returns:
        str: The JSON-formatted string representation of the input value.
        """

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
        Tests the conversion of various JSON strings to their corresponding Python data types using the JSONField's clean method.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `JSONField.clean`: Converts JSON strings to their corresponding Python data types.
        
        Input Variables:
        - `json_string`: A string representing a JSON value.
        
        Output Variables:
        - The converted Python data type corresponding to the input JSON string.
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
        """
        Tests whether the input data has changed.
        
        Args:
        old_value (dict): The original value of the field.
        new_value (str): The new value of the field, represented as a JSON string.
        
        Returns:
        bool: True if the field has changed, False otherwise.
        
        This function uses the `JSONField` class to compare the old and new values of a field. It checks if the old dictionary has been modified when compared to the new JSON string representation of the same
        """

        field = JSONField()
        self.assertIs(field.has_changed({'a': True}, '{"a": 1}'), True)
        self.assertIs(field.has_changed({'a': 1, 'b': 2}, '{"b": 2, "a": 1}'), False)

    def test_custom_encoder_decoder(self):
        """
        Tests the custom JSON encoder and decoder for a JSONField.
        
        This test ensures that the `CustomDecoder` correctly converts UUID strings
        back into UUID objects during deserialization. The `DjangoJSONEncoder`
        is used to serialize the input dictionary with a UUID, and the custom
        decoder is responsible for converting the serialized UUID string back
        into a UUID object.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `CustomDecoder`: A
        """

        class CustomDecoder(json.JSONDecoder):
            def __init__(self, object_hook=None, *args, **kwargs):
                return super().__init__(object_hook=self.as_uuid, *args, **kwargs)

            def as_uuid(self, dct):
                """
                Converts the 'uuid' field in the given dictionary to a UUID object if present.
                
                Args:
                dct (dict): The input dictionary containing the 'uuid' field.
                
                Returns:
                dict: The modified dictionary with the 'uuid' field converted to a UUID object if present.
                """

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
        
        This function creates an instance of a form with a disabled JSONField and checks if the initial value is correctly displayed in the form's HTML output.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - JSONField: Creates a field that accepts JSON data.
        - Form: Base class for creating forms.
        - as_p: Renders the form as an HTML paragraph.
        
        Variables Affected:
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
