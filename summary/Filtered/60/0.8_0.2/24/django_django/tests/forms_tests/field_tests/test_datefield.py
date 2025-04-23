from datetime import date, datetime

from django.forms import (
    DateField, Form, HiddenInput, SelectDateWidget, ValidationError,
)
from django.test import SimpleTestCase, override_settings
from django.utils import translation


class GetDate(Form):
    mydate = DateField(widget=SelectDateWidget)


class DateFieldTest(SimpleTestCase):

    def test_form_field(self):
        a = GetDate({'mydate_month': '4', 'mydate_day': '1', 'mydate_year': '2008'})
        self.assertTrue(a.is_valid())
        self.assertEqual(a.cleaned_data['mydate'], date(2008, 4, 1))

        # As with any widget that implements get_value_from_datadict(), we must
        # accept the input from the "as_hidden" rendering as well.
        self.assertHTMLEqual(
            a['mydate'].as_hidden(),
            '<input type="hidden" name="mydate" value="2008-04-01" id="id_mydate">',
        )

        b = GetDate({'mydate': '2008-4-1'})
        self.assertTrue(b.is_valid())
        self.assertEqual(b.cleaned_data['mydate'], date(2008, 4, 1))

        # Invalid dates shouldn't be allowed
        c = GetDate({'mydate_month': '2', 'mydate_day': '31', 'mydate_year': '2010'})
        self.assertFalse(c.is_valid())
        self.assertEqual(c.errors, {'mydate': ['Enter a valid date.']})

        # label tag is correctly associated with month dropdown
        d = GetDate({'mydate_month': '1', 'mydate_day': '1', 'mydate_year': '2010'})
        self.assertIn('<label for="id_mydate_month">', d.as_p())

    @override_settings(USE_L10N=True)
    @translation.override('nl')
    def test_l10n_date_changed(self):
        """
        DateField.has_changed() with SelectDateWidget works with a localized
        date format (#17165).
        """
        # With Field.show_hidden_initial=False
        b = GetDate({
            'mydate_year': '2008',
            'mydate_month': '4',
            'mydate_day': '1',
        }, initial={'mydate': date(2008, 4, 1)})
        self.assertFalse(b.has_changed())

        b = GetDate({
            'mydate_year': '2008',
            'mydate_month': '4',
            'mydate_day': '2',
        }, initial={'mydate': date(2008, 4, 1)})
        self.assertTrue(b.has_changed())

        # With Field.show_hidden_initial=True
        class GetDateShowHiddenInitial(Form):
            mydate = DateField(widget=SelectDateWidget, show_hidden_initial=True)

        b = GetDateShowHiddenInitial({
            'mydate_year': '2008',
            'mydate_month': '4',
            'mydate_day': '1',
            'initial-mydate': HiddenInput().format_value(date(2008, 4, 1)),
        }, initial={'mydate': date(2008, 4, 1)})
        self.assertFalse(b.has_changed())

        b = GetDateShowHiddenInitial({
            'mydate_year': '2008',
            'mydate_month': '4',
            'mydate_day': '22',
            'initial-mydate': HiddenInput().format_value(date(2008, 4, 1)),
        }, initial={'mydate': date(2008, 4, 1)})
        self.assertTrue(b.has_changed())

        b = GetDateShowHiddenInitial({
            'mydate_year': '2008',
            'mydate_month': '4',
            'mydate_day': '22',
            'initial-mydate': HiddenInput().format_value(date(2008, 4, 1)),
        }, initial={'mydate': date(2008, 4, 22)})
        self.assertTrue(b.has_changed())

        b = GetDateShowHiddenInitial({
            'mydate_year': '2008',
            'mydate_month': '4',
            'mydate_day': '22',
            'initial-mydate': HiddenInput().format_value(date(2008, 4, 22)),
        }, initial={'mydate': date(2008, 4, 1)})
        self.assertFalse(b.has_changed())

    @override_settings(USE_L10N=True)
    @translation.override('nl')
    def test_l10n_invalid_date_in(self):
        """
        Tests the validation of an invalid date input.
        
        This function checks if the `GetDate` class correctly identifies and handles invalid dates. It specifically tests whether the class allows only valid dates and returns an error message for invalid ones.
        
        Parameters:
        None (This function is typically called internally and does not take any parameters).
        
        Returns:
        None (This function performs assertions and does not return any value).
        
        Key Points:
        - The function creates an instance of `GetDate` with a month of '2',
        """

        # Invalid dates shouldn't be allowed
        a = GetDate({'mydate_month': '2', 'mydate_day': '31', 'mydate_year': '2010'})
        self.assertFalse(a.is_valid())
        # 'Geef een geldige datum op.' = 'Enter a valid date.'
        self.assertEqual(a.errors, {'mydate': ['Voer een geldige datum in.']})

    @override_settings(USE_L10N=True)
    @translation.override('nl')
    def test_form_label_association(self):
        """
        Tests the association of form labels with rendered dropdowns.
        
        This function creates an instance of the GetDate class with specified date parameters and checks if the generated HTML includes a label tag correctly associated with the first rendered dropdown.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Elements:
        - `GetDate`: A class that generates HTML for a date input form.
        - `as_p()`: A method that returns the form as a paragraph of HTML.
        - `assertIn`: A method
        """

        # label tag is correctly associated with first rendered dropdown
        a = GetDate({'mydate_month': '1', 'mydate_day': '1', 'mydate_year': '2010'})
        self.assertIn('<label for="id_mydate_day">', a.as_p())

    def test_datefield_1(self):
        f = DateField()
        self.assertEqual(date(2006, 10, 25), f.clean(date(2006, 10, 25)))
        self.assertEqual(date(2006, 10, 25), f.clean(datetime(2006, 10, 25, 14, 30)))
        self.assertEqual(date(2006, 10, 25), f.clean(datetime(2006, 10, 25, 14, 30, 59)))
        self.assertEqual(date(2006, 10, 25), f.clean(datetime(2006, 10, 25, 14, 30, 59, 200)))
        self.assertEqual(date(2006, 10, 25), f.clean('2006-10-25'))
        self.assertEqual(date(2006, 10, 25), f.clean('10/25/2006'))
        self.assertEqual(date(2006, 10, 25), f.clean('10/25/06'))
        self.assertEqual(date(2006, 10, 25), f.clean('Oct 25 2006'))
        self.assertEqual(date(2006, 10, 25), f.clean('October 25 2006'))
        self.assertEqual(date(2006, 10, 25), f.clean('October 25, 2006'))
        self.assertEqual(date(2006, 10, 25), f.clean('25 October 2006'))
        self.assertEqual(date(2006, 10, 25), f.clean('25 October, 2006'))
        with self.assertRaisesMessage(ValidationError, "'Enter a valid date.'"):
            f.clean('2006-4-31')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid date.'"):
            f.clean('200a-10-25')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid date.'"):
            f.clean('25/10/06')
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None)

    def test_datefield_2(self):
        f = DateField(required=False)
        self.assertIsNone(f.clean(None))
        self.assertEqual('None', repr(f.clean(None)))
        self.assertIsNone(f.clean(''))
        self.assertEqual('None', repr(f.clean('')))

    def test_datefield_3(self):
        """
        Tests the DateField with custom input format '%Y %m %d'.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key behaviors:
        - Validates and returns a date object when the input matches the format '%Y %m %d'.
        - Accepts date and datetime objects as valid inputs.
        - Converts a string in the format '2006 10 25' to a date object.
        - Raises a ValidationError with the message "'Enter a valid date.'" for inputs that do
        """

        f = DateField(input_formats=['%Y %m %d'])
        self.assertEqual(date(2006, 10, 25), f.clean(date(2006, 10, 25)))
        self.assertEqual(date(2006, 10, 25), f.clean(datetime(2006, 10, 25, 14, 30)))
        self.assertEqual(date(2006, 10, 25), f.clean('2006 10 25'))
        with self.assertRaisesMessage(ValidationError, "'Enter a valid date.'"):
            f.clean('2006-10-25')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid date.'"):
            f.clean('10/25/2006')
        with self.assertRaisesMessage(ValidationError, "'Enter a valid date.'"):
            f.clean('10/25/06')

    def test_datefield_4(self):
        # Test whitespace stripping behavior (#5714)
        f = DateField()
        self.assertEqual(date(2006, 10, 25), f.clean(' 10/25/2006 '))
        self.assertEqual(date(2006, 10, 25), f.clean(' 10/25/06 '))
        self.assertEqual(date(2006, 10, 25), f.clean(' Oct 25   2006 '))
        self.assertEqual(date(2006, 10, 25), f.clean(' October  25 2006 '))
        self.assertEqual(date(2006, 10, 25), f.clean(' October 25, 2006 '))
        self.assertEqual(date(2006, 10, 25), f.clean(' 25 October 2006 '))
        with self.assertRaisesMessage(ValidationError, "'Enter a valid date.'"):
            f.clean('   ')

    def test_datefield_5(self):
        # Test null bytes (#18982)
        f = DateField()
        with self.assertRaisesMessage(ValidationError, "'Enter a valid date.'"):
            f.clean('a\x00b')

    def test_datefield_changed(self):
        format = '%d/%m/%Y'
        f = DateField(input_formats=[format])
        d = date(2007, 9, 17)
        self.assertFalse(f.has_changed(d, '17/09/2007'))

    def test_datefield_strptime(self):
        """field.strptime() doesn't raise a UnicodeEncodeError (#16123)"""
        f = DateField()
        try:
            f.strptime('31 мая 2011', '%d-%b-%y')
        except Exception as e:
            # assertIsInstance or assertRaises cannot be used because UnicodeEncodeError
            # is a subclass of ValueError
            self.assertEqual(e.__class__, ValueError)
