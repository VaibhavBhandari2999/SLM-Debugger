import logging

from django.template import Engine, Variable, VariableDoesNotExist
from django.test import SimpleTestCase


class VariableResolveLoggingTests(SimpleTestCase):
    loglevel = logging.DEBUG

    def test_log_on_variable_does_not_exist_silent(self):
        """
        Tests the logging behavior when a variable does not exist in a template context.
        
        This function checks that when a variable is accessed that does not exist in the provided context, a silent exception is logged without raising the exception. The test uses a custom exception class `SilentDoesNotExist` which inherits from `Exception` and sets `silent_variable_failure` to `True`.
        
        Key Parameters:
        - `self`: The test case instance.
        
        Key Attributes of the `TestObject`:
        - `template_name`: A
        """

        class TestObject:
            class SilentDoesNotExist(Exception):
                silent_variable_failure = True

            @property
            def template_name(self):
                return "template_name"

            @property
            def template(self):
                return Engine().from_string('')

            @property
            def article(self):
                raise TestObject.SilentDoesNotExist("Attribute does not exist.")

            def __iter__(self):
                return (attr for attr in dir(TestObject) if attr[:2] != "__")

            def __getitem__(self, item):
                return self.__dict__[item]

        with self.assertLogs('django.template', self.loglevel) as cm:
            Variable('article').resolve(TestObject())

        self.assertEqual(len(cm.records), 1)
        log_record = cm.records[0]
        self.assertEqual(
            log_record.getMessage(),
            "Exception while resolving variable 'article' in template 'template_name'."
        )
        self.assertIsNotNone(log_record.exc_info)
        raised_exception = log_record.exc_info[1]
        self.assertEqual(str(raised_exception), 'Attribute does not exist.')

    def test_log_on_variable_does_not_exist_not_silent(self):
        """
        Tests the logging behavior when a variable does not exist during template rendering.
        
        This function asserts that a `VariableDoesNotExist` exception is raised and that a log message is generated. The log message indicates that an exception occurred while resolving a variable in a template, and it includes details about the exception.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        VariableDoesNotExist: If the variable does not exist in the context.
        
        Logs:
        A log message is generated with the following details:
        """

        with self.assertLogs('django.template', self.loglevel) as cm:
            with self.assertRaises(VariableDoesNotExist):
                Variable('article.author').resolve({'article': {'section': 'News'}})

        self.assertEqual(len(cm.records), 1)
        log_record = cm.records[0]
        self.assertEqual(
            log_record.getMessage(),
            "Exception while resolving variable 'author' in template 'unknown'."
        )
        self.assertIsNotNone(log_record.exc_info)
        raised_exception = log_record.exc_info[1]
        self.assertEqual(
            str(raised_exception),
            "Failed lookup for key [author] in {'section': 'News'}"
        )

    def test_no_log_when_variable_exists(self):
        with self.assertNoLogs('django.template', self.loglevel):
            Variable('article.section').resolve({'article': {'section': 'News'}})
