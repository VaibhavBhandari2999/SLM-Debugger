from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import (
    BooleanField, CharField, ChoiceField, DateField, DateTimeField,
    DecimalField, EmailField, FileField, FloatField, Form,
    GenericIPAddressField, IntegerField, ModelChoiceField,
    ModelMultipleChoiceField, MultipleChoiceField, RegexField,
    SplitDateTimeField, TimeField, URLField, utils,
)
from django.template import Context, Template
from django.test import SimpleTestCase, TestCase, ignore_warnings
from django.utils.deprecation import RemovedInDjango40Warning
from django.utils.safestring import mark_safe

from ..models import ChoiceModel


class AssertFormErrorsMixin:
    def assertFormErrors(self, expected, the_callable, *args, **kwargs):
        """
        Assert that a callable raises a ValidationError with the expected error messages.
        
        Parameters:
        expected (list): A list of expected error messages.
        the_callable (function): The callable to test.
        *args: Positional arguments to pass to the_callable.
        **kwargs: Keyword arguments to pass to the_callable.
        
        Raises:
        ValidationError: If the_callable does not raise ValidationError or if the error messages do not match the expected ones.
        
        Example usage:
        expected = ['This field is required.', '
        """

        with self.assertRaises(ValidationError) as cm:
            the_callable(*args, **kwargs)
        self.assertEqual(cm.exception.messages, expected)


class FormsErrorMessagesTestCase(SimpleTestCase, AssertFormErrorsMixin):
    def test_charfield(self):
        e = {
            'required': 'REQUIRED',
            'min_length': 'LENGTH %(show_value)s, MIN LENGTH %(limit_value)s',
            'max_length': 'LENGTH %(show_value)s, MAX LENGTH %(limit_value)s',
        }
        f = CharField(min_length=5, max_length=10, error_messages=e)
        self.assertFormErrors(['REQUIRED'], f.clean, '')
        self.assertFormErrors(['LENGTH 4, MIN LENGTH 5'], f.clean, '1234')
        self.assertFormErrors(['LENGTH 11, MAX LENGTH 10'], f.clean, '12345678901')

    def test_integerfield(self):
        e = {
            'required': 'REQUIRED',
            'invalid': 'INVALID',
            'min_value': 'MIN VALUE IS %(limit_value)s',
            'max_value': 'MAX VALUE IS %(limit_value)s',
        }
        f = IntegerField(min_value=5, max_value=10, error_messages=e)
        self.assertFormErrors(['REQUIRED'], f.clean, '')
        self.assertFormErrors(['INVALID'], f.clean, 'abc')
        self.assertFormErrors(['MIN VALUE IS 5'], f.clean, '4')
        self.assertFormErrors(['MAX VALUE IS 10'], f.clean, '11')

    def test_floatfield(self):
        """
        Test the behavior of a FloatField in a form.
        
        This function tests the FloatField with various inputs to ensure it behaves as expected. The FloatField is configured with specific error messages and constraints (min_value and max_value).
        
        Parameters:
        - f: A FloatField instance with min_value set to 5 and max_value set to 10, and custom error messages.
        
        Returns:
        - None: This function asserts expected errors for different input values and does not return any value.
        
        Key Parameters:
        -
        """

        e = {
            'required': 'REQUIRED',
            'invalid': 'INVALID',
            'min_value': 'MIN VALUE IS %(limit_value)s',
            'max_value': 'MAX VALUE IS %(limit_value)s',
        }
        f = FloatField(min_value=5, max_value=10, error_messages=e)
        self.assertFormErrors(['REQUIRED'], f.clean, '')
        self.assertFormErrors(['INVALID'], f.clean, 'abc')
        self.assertFormErrors(['MIN VALUE IS 5'], f.clean, '4')
        self.assertFormErrors(['MAX VALUE IS 10'], f.clean, '11')

    def test_decimalfield(self):
        e = {
            'required': 'REQUIRED',
            'invalid': 'INVALID',
            'min_value': 'MIN VALUE IS %(limit_value)s',
            'max_value': 'MAX VALUE IS %(limit_value)s',
            'max_digits': 'MAX DIGITS IS %(max)s',
            'max_decimal_places': 'MAX DP IS %(max)s',
            'max_whole_digits': 'MAX DIGITS BEFORE DP IS %(max)s',
        }
        f = DecimalField(min_value=5, max_value=10, error_messages=e)
        self.assertFormErrors(['REQUIRED'], f.clean, '')
        self.assertFormErrors(['INVALID'], f.clean, 'abc')
        self.assertFormErrors(['MIN VALUE IS 5'], f.clean, '4')
        self.assertFormErrors(['MAX VALUE IS 10'], f.clean, '11')

        f2 = DecimalField(max_digits=4, decimal_places=2, error_messages=e)
        self.assertFormErrors(['MAX DIGITS IS 4'], f2.clean, '123.45')
        self.assertFormErrors(['MAX DP IS 2'], f2.clean, '1.234')
        self.assertFormErrors(['MAX DIGITS BEFORE DP IS 2'], f2.clean, '123.4')

    def test_datefield(self):
        """
        Tests the behavior of the DateField in a form.
        
        This function tests the DateField to ensure it behaves as expected under different conditions. The DateField is configured with a set of error messages for validation purposes. The function checks if the field correctly identifies required and invalid inputs.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - `e`: A dictionary containing error messages for required and invalid inputs.
        
        Keywords:
        - `f`: An instance of the DateField configured with the
        """

        e = {
            'required': 'REQUIRED',
            'invalid': 'INVALID',
        }
        f = DateField(error_messages=e)
        self.assertFormErrors(['REQUIRED'], f.clean, '')
        self.assertFormErrors(['INVALID'], f.clean, 'abc')

    def test_timefield(self):
        e = {
            'required': 'REQUIRED',
            'invalid': 'INVALID',
        }
        f = TimeField(error_messages=e)
        self.assertFormErrors(['REQUIRED'], f.clean, '')
        self.assertFormErrors(['INVALID'], f.clean, 'abc')

    def test_datetimefield(self):
        e = {
            'required': 'REQUIRED',
            'invalid': 'INVALID',
        }
        f = DateTimeField(error_messages=e)
        self.assertFormErrors(['REQUIRED'], f.clean, '')
        self.assertFormErrors(['INVALID'], f.clean, 'abc')

    def test_regexfield(self):
        e = {
            'required': 'REQUIRED',
            'invalid': 'INVALID',
            'min_length': 'LENGTH %(show_value)s, MIN LENGTH %(limit_value)s',
            'max_length': 'LENGTH %(show_value)s, MAX LENGTH %(limit_value)s',
        }
        f = RegexField(r'^[0-9]+$', min_length=5, max_length=10, error_messages=e)
        self.assertFormErrors(['REQUIRED'], f.clean, '')
        self.assertFormErrors(['INVALID'], f.clean, 'abcde')
        self.assertFormErrors(['LENGTH 4, MIN LENGTH 5'], f.clean, '1234')
        self.assertFormErrors(['LENGTH 11, MAX LENGTH 10'], f.clean, '12345678901')

    def test_emailfield(self):
        """
        Test the EmailField with various error conditions.
        
        This function tests the EmailField with different error messages and constraints. It checks for required fields, invalid email formats, and length constraints.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - `e`: A dictionary containing custom error messages for different validation conditions.
        
        Key Keywords:
        - `f`: An instance of the EmailField with specified constraints (min_length, max_length) and custom error messages.
        
        Test Cases:
        - Tests
        """

        e = {
            'required': 'REQUIRED',
            'invalid': 'INVALID',
            'min_length': 'LENGTH %(show_value)s, MIN LENGTH %(limit_value)s',
            'max_length': 'LENGTH %(show_value)s, MAX LENGTH %(limit_value)s',
        }
        f = EmailField(min_length=8, max_length=10, error_messages=e)
        self.assertFormErrors(['REQUIRED'], f.clean, '')
        self.assertFormErrors(['INVALID'], f.clean, 'abcdefgh')
        self.assertFormErrors(['LENGTH 7, MIN LENGTH 8'], f.clean, 'a@b.com')
        self.assertFormErrors(['LENGTH 11, MAX LENGTH 10'], f.clean, 'aye@bee.com')

    def test_filefield(self):
        e = {
            'required': 'REQUIRED',
            'invalid': 'INVALID',
            'missing': 'MISSING',
            'empty': 'EMPTY FILE',
        }
        f = FileField(error_messages=e)
        self.assertFormErrors(['REQUIRED'], f.clean, '')
        self.assertFormErrors(['INVALID'], f.clean, 'abc')
        self.assertFormErrors(['EMPTY FILE'], f.clean, SimpleUploadedFile('name', None))
        self.assertFormErrors(['EMPTY FILE'], f.clean, SimpleUploadedFile('name', ''))

    def test_urlfield(self):
        """
        Test the URLField validation.
        
        This function tests the URLField with different error messages and validation rules. The URLField is configured with specific error messages and a maximum length of 17 characters. The function validates the field with empty, invalid, and long URLs to ensure that the correct error messages are raised.
        
        Parameters:
        - f (URLField): The URLField instance to be tested.
        
        Returns:
        - None: The function asserts the expected errors for each test case.
        
        Key Parameters:
        - error_messages
        """

        e = {
            'required': 'REQUIRED',
            'invalid': 'INVALID',
            'max_length': '"%(value)s" has more than %(limit_value)d characters.',
        }
        f = URLField(error_messages=e, max_length=17)
        self.assertFormErrors(['REQUIRED'], f.clean, '')
        self.assertFormErrors(['INVALID'], f.clean, 'abc.c')
        self.assertFormErrors(
            ['"http://djangoproject.com" has more than 17 characters.'],
            f.clean,
            'djangoproject.com'
        )

    def test_booleanfield(self):
        e = {
            'required': 'REQUIRED',
        }
        f = BooleanField(error_messages=e)
        self.assertFormErrors(['REQUIRED'], f.clean, '')

    def test_choicefield(self):
        e = {
            'required': 'REQUIRED',
            'invalid_choice': '%(value)s IS INVALID CHOICE',
        }
        f = ChoiceField(choices=[('a', 'aye')], error_messages=e)
        self.assertFormErrors(['REQUIRED'], f.clean, '')
        self.assertFormErrors(['b IS INVALID CHOICE'], f.clean, 'b')

    def test_multiplechoicefield(self):
        """
        Test the behavior of a MultipleChoiceField in a form.
        
        This function tests the MultipleChoiceField with different inputs and error messages. The field is configured with a list of choices and custom error messages for required, invalid choice, and invalid list errors.
        
        Parameters:
        - f (MultipleChoiceField): The MultipleChoiceField instance to test.
        
        Returns:
        - None: The function asserts the expected errors for each test case.
        
        Key Parameters:
        - choices (list): A list of tuples representing the choices for the
        """

        e = {
            'required': 'REQUIRED',
            'invalid_choice': '%(value)s IS INVALID CHOICE',
            'invalid_list': 'NOT A LIST',
        }
        f = MultipleChoiceField(choices=[('a', 'aye')], error_messages=e)
        self.assertFormErrors(['REQUIRED'], f.clean, '')
        self.assertFormErrors(['NOT A LIST'], f.clean, 'b')
        self.assertFormErrors(['b IS INVALID CHOICE'], f.clean, ['b'])

    def test_splitdatetimefield(self):
        e = {
            'required': 'REQUIRED',
            'invalid_date': 'INVALID DATE',
            'invalid_time': 'INVALID TIME',
        }
        f = SplitDateTimeField(error_messages=e)
        self.assertFormErrors(['REQUIRED'], f.clean, '')
        self.assertFormErrors(['INVALID DATE', 'INVALID TIME'], f.clean, ['a', 'b'])

    def test_generic_ipaddressfield(self):
        """
        Tests the behavior of the GenericIPAddressField in Django forms.
        
        This function tests the validation of the GenericIPAddressField with different error messages and invalid input values. The field is configured with specific error messages for required and invalid IP address scenarios. The function asserts that the field raises the correct error messages when provided with empty or invalid IP address strings.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - error_messages (dict): A dictionary containing custom error messages for required and invalid IP address
        """

        e = {
            'required': 'REQUIRED',
            'invalid': 'INVALID IP ADDRESS',
        }
        f = GenericIPAddressField(error_messages=e)
        self.assertFormErrors(['REQUIRED'], f.clean, '')
        self.assertFormErrors(['INVALID IP ADDRESS'], f.clean, '127.0.0')

    def test_subclassing_errorlist(self):
        class TestForm(Form):
            first_name = CharField()
            last_name = CharField()
            birthday = DateField()

            def clean(self):
                raise ValidationError("I like to be awkward.")

        class CustomErrorList(utils.ErrorList):
            def __str__(self):
                return self.as_divs()

            def as_divs(self):
                if not self:
                    return ''
                return mark_safe('<div class="error">%s</div>' % ''.join('<p>%s</p>' % e for e in self))

        # This form should print errors the default way.
        form1 = TestForm({'first_name': 'John'})
        self.assertHTMLEqual(
            str(form1['last_name'].errors),
            '<ul class="errorlist"><li>This field is required.</li></ul>'
        )
        self.assertHTMLEqual(
            str(form1.errors['__all__']),
            '<ul class="errorlist nonfield"><li>I like to be awkward.</li></ul>'
        )

        # This one should wrap error groups in the customized way.
        form2 = TestForm({'first_name': 'John'}, error_class=CustomErrorList)
        self.assertHTMLEqual(str(form2['last_name'].errors), '<div class="error"><p>This field is required.</p></div>')
        self.assertHTMLEqual(str(form2.errors['__all__']), '<div class="error"><p>I like to be awkward.</p></div>')

    def test_error_messages_escaping(self):
        # The forms layer doesn't escape input values directly because error
        # messages might be presented in non-HTML contexts. Instead, the
        # message is marked for escaping by the template engine, so a template
        # is needed to trigger the escaping.
        t = Template('{{ form.errors }}')

        class SomeForm(Form):
            field = ChoiceField(choices=[('one', 'One')])

        f = SomeForm({'field': '<script>'})
        self.assertHTMLEqual(
            t.render(Context({'form': f})),
            '<ul class="errorlist"><li>field<ul class="errorlist">'
            '<li>Select a valid choice. &lt;script&gt; is not one of the '
            'available choices.</li></ul></li></ul>'
        )

        class SomeForm(Form):
            field = MultipleChoiceField(choices=[('one', 'One')])

        f = SomeForm({'field': ['<script>']})
        self.assertHTMLEqual(
            t.render(Context({'form': f})),
            '<ul class="errorlist"><li>field<ul class="errorlist">'
            '<li>Select a valid choice. &lt;script&gt; is not one of the '
            'available choices.</li></ul></li></ul>'
        )

        class SomeForm(Form):
            field = ModelMultipleChoiceField(ChoiceModel.objects.all())

        f = SomeForm({'field': ['<script>']})
        self.assertHTMLEqual(
            t.render(Context({'form': f})),
            '<ul class="errorlist"><li>field<ul class="errorlist">'
            '<li>“&lt;script&gt;” is not a valid value.</li>'
            '</ul></li></ul>'
        )


class ModelChoiceFieldErrorMessagesTestCase(TestCase, AssertFormErrorsMixin):
    def test_modelchoicefield(self):
        # Create choices for the model choice field tests below.
        ChoiceModel.objects.create(pk=1, name='a')
        ChoiceModel.objects.create(pk=2, name='b')
        ChoiceModel.objects.create(pk=3, name='c')

        # ModelChoiceField
        e = {
            'required': 'REQUIRED',
            'invalid_choice': 'INVALID CHOICE',
        }
        f = ModelChoiceField(queryset=ChoiceModel.objects.all(), error_messages=e)
        self.assertFormErrors(['REQUIRED'], f.clean, '')
        self.assertFormErrors(['INVALID CHOICE'], f.clean, '4')

        # ModelMultipleChoiceField
        e = {
            'required': 'REQUIRED',
            'invalid_choice': '%(value)s IS INVALID CHOICE',
            'invalid_list': 'NOT A LIST OF VALUES',
        }
        f = ModelMultipleChoiceField(queryset=ChoiceModel.objects.all(), error_messages=e)
        self.assertFormErrors(['REQUIRED'], f.clean, '')
        self.assertFormErrors(['NOT A LIST OF VALUES'], f.clean, '3')
        self.assertFormErrors(['4 IS INVALID CHOICE'], f.clean, ['4'])


class DeprecationTests(TestCase, AssertFormErrorsMixin):
    @ignore_warnings(category=RemovedInDjango40Warning)
    def test_list_error_message(self):
        f = ModelMultipleChoiceField(
            queryset=ChoiceModel.objects.all(),
            error_messages={'list': 'NOT A LIST OF VALUES'},
        )
        self.assertFormErrors(['NOT A LIST OF VALUES'], f.clean, '3')

    def test_list_error_message_warning(self):
        """
        Tests the behavior of the 'list' error message key in ModelMultipleChoiceField.
        
        This function asserts that using the 'list' error message key raises a RemovedInDjango40Warning with a specific message. The key 'list' is deprecated and should be replaced with 'invalid_list'.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Raises:
        - RemovedInDjango40Warning: If the 'list' error message key is used, a warning is raised with the message
        """

        msg = (
            "The 'list' error message key is deprecated in favor of "
            "'invalid_list'."
        )
        with self.assertRaisesMessage(RemovedInDjango40Warning, msg):
            ModelMultipleChoiceField(
                queryset=ChoiceModel.objects.all(),
                error_messages={'list': 'NOT A LIST OF VALUES'},
            )
