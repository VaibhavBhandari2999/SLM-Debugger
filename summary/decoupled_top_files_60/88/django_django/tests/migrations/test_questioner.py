import datetime
from unittest import mock

from django.db.migrations.questioner import (
    InteractiveMigrationQuestioner, MigrationQuestioner,
)
from django.db.models import NOT_PROVIDED
from django.test import SimpleTestCase
from django.test.utils import captured_stdout, override_settings


class QuestionerTests(SimpleTestCase):
    @override_settings(
        INSTALLED_APPS=['migrations'],
        MIGRATION_MODULES={'migrations': None},
    )
    def test_ask_initial_with_disabled_migrations(self):
        questioner = MigrationQuestioner()
        self.assertIs(False, questioner.ask_initial('migrations'))

    def test_ask_not_null_alteration(self):
        questioner = MigrationQuestioner()
        self.assertIsNone(questioner.ask_not_null_alteration('field_name', 'model_name'))

    @mock.patch('builtins.input', return_value='2')
    def test_ask_not_null_alteration_not_provided(self, mock):
        """
        Ask the user if a field should be altered to NOT NULL.
        
        This method prompts the user for input to determine if a field in a model should be altered to NOT NULL. If the user does not provide an answer, the method returns NOT_PROVIDED.
        
        Parameters:
        field_name (str): The name of the field to be altered.
        model_name (str): The name of the model containing the field.
        
        Returns:
        object: NOT_PROVIDED if the user does not provide an answer,
        """

        questioner = InteractiveMigrationQuestioner()
        with captured_stdout():
            question = questioner.ask_not_null_alteration('field_name', 'model_name')
        self.assertEqual(question, NOT_PROVIDED)


class QuestionerHelperMethodsTests(SimpleTestCase):
    questioner = InteractiveMigrationQuestioner()

    @mock.patch('builtins.input', return_value='datetime.timedelta(days=1)')
    def test_questioner_default_timedelta(self, mock_input):
        questioner = InteractiveMigrationQuestioner()
        with captured_stdout():
            value = questioner._ask_default()
        self.assertEqual(value, datetime.timedelta(days=1))

    @mock.patch('builtins.input', return_value='')
    def test_questioner_default_no_user_entry(self, mock_input):
        with captured_stdout():
            value = self.questioner._ask_default(default='datetime.timedelta(days=1)')
        self.assertEqual(value, datetime.timedelta(days=1))

    @mock.patch('builtins.input', side_effect=['', 'exit'])
    def test_questioner_no_default_no_user_entry(self, mock_input):
        """
        Tests the `_ask_default` method of the `Questioner` class without a default value and without user input.
        
        Parameters:
        - mock_input (unittest.mock.Mock): A mock object to simulate user input.
        
        Raises:
        - SystemExit: If the user does not provide any input, the method will raise SystemExit.
        
        Expected Behavior:
        - The method should prompt the user to enter some code or 'exit' to exit.
        - If no input is provided, a SystemExit exception is raised.
        - The
        """

        with captured_stdout() as stdout, self.assertRaises(SystemExit):
            self.questioner._ask_default()
        self.assertIn(
            "Please enter some code, or 'exit' (without quotes) to exit.",
            stdout.getvalue(),
        )

    @mock.patch('builtins.input', side_effect=['bad code', 'exit'])
    def test_questioner_no_default_bad_user_entry_code(self, mock_input):
        with captured_stdout() as stdout, self.assertRaises(SystemExit):
            self.questioner._ask_default()
        self.assertIn('Invalid input: ', stdout.getvalue())

    @mock.patch('builtins.input', side_effect=['', 'n'])
    def test_questioner_no_default_no_user_entry_boolean(self, mock_input):
        """
        Tests the boolean input functionality of the questioner without a default value and no user input.
        
        Parameters:
        mock_input (unittest.mock.Mock): A mock object to simulate user input.
        
        Returns:
        None: This function does not return any value. It asserts that the boolean input returns False.
        """

        with captured_stdout():
            value = self.questioner._boolean_input('Proceed?')
        self.assertIs(value, False)

    @mock.patch('builtins.input', return_value='')
    def test_questioner_default_no_user_entry_boolean(self, mock_input):
        """
        Tests the boolean input functionality of the questioner with a default value of True.
        
        This function tests the `_boolean_input` method of the `questioner` object to ensure it returns the default value when no user input is provided.
        
        Parameters:
        - mock_input: A mock object for the user input.
        
        Returns:
        - None: The function asserts the expected behavior but does not return any value.
        
        Key Points:
        - The method checks if the user input is provided or not.
        - If no input is provided
        """

        with captured_stdout():
            value = self.questioner._boolean_input('Proceed?', default=True)
        self.assertIs(value, True)

    @mock.patch('builtins.input', side_effect=[10, 'garbage', 1])
    def test_questioner_bad_user_choice(self, mock_input):
        question = 'Make a choice:'
        with captured_stdout() as stdout:
            value = self.questioner._choice_input(question, choices='abc')
        expected_msg = (
            f'{question}\n'
            f' 1) a\n'
            f' 2) b\n'
            f' 3) c\n'
        )
        self.assertIn(expected_msg, stdout.getvalue())
        self.assertEqual(value, 1)
f.assertEqual(value, 1)
