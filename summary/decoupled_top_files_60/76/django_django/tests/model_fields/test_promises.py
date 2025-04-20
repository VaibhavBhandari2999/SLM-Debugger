import datetime
from decimal import Decimal

from django.db.models import (
    AutoField, BinaryField, BooleanField, CharField, DateField, DateTimeField,
    DecimalField, EmailField, FileField, FilePathField, FloatField,
    GenericIPAddressField, ImageField, IntegerField, IPAddressField,
    PositiveBigIntegerField, PositiveIntegerField, PositiveSmallIntegerField,
    SlugField, SmallIntegerField, TextField, TimeField, URLField,
)
from django.test import SimpleTestCase
from django.utils.functional import lazy


class PromiseTest(SimpleTestCase):

    def test_AutoField(self):
        lazy_func = lazy(lambda: 1, int)
        self.assertIsInstance(AutoField(primary_key=True).get_prep_value(lazy_func()), int)

    def test_BinaryField(self):
        lazy_func = lazy(lambda: b'', bytes)
        self.assertIsInstance(BinaryField().get_prep_value(lazy_func()), bytes)

    def test_BooleanField(self):
        lazy_func = lazy(lambda: True, bool)
        self.assertIsInstance(BooleanField().get_prep_value(lazy_func()), bool)

    def test_CharField(self):
        lazy_func = lazy(lambda: '', str)
        self.assertIsInstance(CharField().get_prep_value(lazy_func()), str)
        lazy_func = lazy(lambda: 0, int)
        self.assertIsInstance(CharField().get_prep_value(lazy_func()), str)

    def test_DateField(self):
        lazy_func = lazy(lambda: datetime.date.today(), datetime.date)
        self.assertIsInstance(DateField().get_prep_value(lazy_func()), datetime.date)

    def test_DateTimeField(self):
        lazy_func = lazy(lambda: datetime.datetime.now(), datetime.datetime)
        self.assertIsInstance(DateTimeField().get_prep_value(lazy_func()), datetime.datetime)

    def test_DecimalField(self):
        lazy_func = lazy(lambda: Decimal('1.2'), Decimal)
        self.assertIsInstance(DecimalField().get_prep_value(lazy_func()), Decimal)

    def test_EmailField(self):
        lazy_func = lazy(lambda: 'mailbox@domain.com', str)
        self.assertIsInstance(EmailField().get_prep_value(lazy_func()), str)

    def test_FileField(self):
        """
        Tests the behavior of the FileField's get_prep_value method.
        
        This method checks how the FileField handles different types of input, specifically when the input is a lazy function. The function expects a lazy function as input and verifies that the output is always a string. Two different lazy functions are tested: one that returns a string and one that returns an integer. The method ensures that the prep value is correctly converted to a string in both cases.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key
        """

        lazy_func = lazy(lambda: 'filename.ext', str)
        self.assertIsInstance(FileField().get_prep_value(lazy_func()), str)
        lazy_func = lazy(lambda: 0, int)
        self.assertIsInstance(FileField().get_prep_value(lazy_func()), str)

    def test_FilePathField(self):
        """
        Tests the FilePathField's get_prep_value method.
        
        This method should return a string when passed a lazy function that returns a string or an integer.
        
        Parameters:
        - lazy_func (lazy function): A lazy function that returns either a string or an integer.
        
        Returns:
        - str: The prepared value, which is always a string.
        
        Key Verifications:
        - The method should handle lazy functions that return strings and convert them to strings.
        - The method should handle lazy functions that return integers and convert them to strings
        """

        lazy_func = lazy(lambda: 'tests.py', str)
        self.assertIsInstance(FilePathField().get_prep_value(lazy_func()), str)
        lazy_func = lazy(lambda: 0, int)
        self.assertIsInstance(FilePathField().get_prep_value(lazy_func()), str)

    def test_FloatField(self):
        lazy_func = lazy(lambda: 1.2, float)
        self.assertIsInstance(FloatField().get_prep_value(lazy_func()), float)

    def test_ImageField(self):
        lazy_func = lazy(lambda: 'filename.ext', str)
        self.assertIsInstance(ImageField().get_prep_value(lazy_func()), str)

    def test_IntegerField(self):
        lazy_func = lazy(lambda: 1, int)
        self.assertIsInstance(IntegerField().get_prep_value(lazy_func()), int)

    def test_IPAddressField(self):
        lazy_func = lazy(lambda: '127.0.0.1', str)
        self.assertIsInstance(IPAddressField().get_prep_value(lazy_func()), str)
        lazy_func = lazy(lambda: 0, int)
        self.assertIsInstance(IPAddressField().get_prep_value(lazy_func()), str)

    def test_GenericIPAddressField(self):
        lazy_func = lazy(lambda: '127.0.0.1', str)
        self.assertIsInstance(GenericIPAddressField().get_prep_value(lazy_func()), str)
        lazy_func = lazy(lambda: 0, int)
        self.assertIsInstance(GenericIPAddressField().get_prep_value(lazy_func()), str)

    def test_PositiveIntegerField(self):
        lazy_func = lazy(lambda: 1, int)
        self.assertIsInstance(PositiveIntegerField().get_prep_value(lazy_func()), int)

    def test_PositiveSmallIntegerField(self):
        lazy_func = lazy(lambda: 1, int)
        self.assertIsInstance(PositiveSmallIntegerField().get_prep_value(lazy_func()), int)

    def test_PositiveBigIntegerField(self):
        lazy_func = lazy(lambda: 1, int)
        self.assertIsInstance(PositiveBigIntegerField().get_prep_value(lazy_func()), int)

    def test_SlugField(self):
        lazy_func = lazy(lambda: 'slug', str)
        self.assertIsInstance(SlugField().get_prep_value(lazy_func()), str)
        lazy_func = lazy(lambda: 0, int)
        self.assertIsInstance(SlugField().get_prep_value(lazy_func()), str)

    def test_SmallIntegerField(self):
        lazy_func = lazy(lambda: 1, int)
        self.assertIsInstance(SmallIntegerField().get_prep_value(lazy_func()), int)

    def test_TextField(self):
        lazy_func = lazy(lambda: 'Abc', str)
        self.assertIsInstance(TextField().get_prep_value(lazy_func()), str)
        lazy_func = lazy(lambda: 0, int)
        self.assertIsInstance(TextField().get_prep_value(lazy_func()), str)

    def test_TimeField(self):
        lazy_func = lazy(lambda: datetime.datetime.now().time(), datetime.time)
        self.assertIsInstance(TimeField().get_prep_value(lazy_func()), datetime.time)

    def test_URLField(self):
        lazy_func = lazy(lambda: 'http://domain.com', str)
        self.assertIsInstance(URLField().get_prep_value(lazy_func()), str)
