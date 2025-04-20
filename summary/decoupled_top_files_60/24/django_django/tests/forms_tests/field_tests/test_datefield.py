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
        """
        Tests for the GetDate form field.
        
        This function tests various aspects of the GetDate form field, including:
        - Valid date input validation and cleaning
        - Hidden input rendering
        - Invalid date input handling
        - Label association with the month dropdown
        
        Parameters:
        - a: A valid date input with month, day, and year.
        - b: A valid date input in the format 'YYYY-MM-DD'.
        - c: An invalid date input with an invalid day for February.
        - d: A valid
        """

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
        # Invalid dates shouldn't be allowed
        a = GetDate({'mydate_month': '2', 'mydate_day': '31', 'mydate_year': '2010'})
        self.assertFalse(a.is_valid())
        # 'Geef een geldige datum op.' = 'Enter a valid date.'
        self.assertEqual(a.errors, {'mydate': ['Voer een geldige datum in.']})

    @override_settings(USE_L10N=True)
    @translation.override('nl')
    def test_form_label_association(self):
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
        """
        Tests the behavior of the DateField when provided with None or empty string inputs.
        
        This function checks the clean method of the DateField class to ensure it correctly handles None and empty string inputs. It verifies that the clean method returns None for both inputs and that the representation of the cleaned value is 'None' in both cases.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Points:
        - The function tests the DateField's clean method with None and empty string inputs.
        - It asserts that the
        """

        f = DateField(required=False)
        self.assertIsNone(f.clean(None))
        self.assertEqual('None', repr(f.clean(None)))
        self.assertIsNone(f.clean(''))
        self.assertEqual('None', repr(f.clean('')))

    def test_datefield_3(self):
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
        """
        Test the validation of a DateField with null bytes.
        
        This function tests the DateField's ability to handle and validate input containing null bytes. It raises a ValidationError if the input is not a valid date.
        
        Parameters:
        None
        
        Raises:
        ValidationError: If the input is not a valid date and contains null bytes.
        
        Key Points:
        - The function uses a DateField instance to clean the input.
        - It expects the input to be a string representing a date.
        - The function checks if the input
        """

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
