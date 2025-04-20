import os.path

from django.forms import FilePathField, ValidationError
from django.test import SimpleTestCase

PATH = os.path.dirname(os.path.abspath(__file__))


def fix_os_paths(x):
    if isinstance(x, str):
        if x.startswith(PATH):
            x = x[len(PATH):]
        return x.replace('\\', '/')
    elif isinstance(x, tuple):
        return tuple(fix_os_paths(list(x)))
    elif isinstance(x, list):
        return [fix_os_paths(y) for y in x]
    else:
        return x


class FilePathFieldTest(SimpleTestCase):
    expected_choices = [
        ('/filepathfield_test_dir/__init__.py', '__init__.py'),
        ('/filepathfield_test_dir/a.py', 'a.py'),
        ('/filepathfield_test_dir/ab.py', 'ab.py'),
        ('/filepathfield_test_dir/b.py', 'b.py'),
        ('/filepathfield_test_dir/c/__init__.py', '__init__.py'),
        ('/filepathfield_test_dir/c/d.py', 'd.py'),
        ('/filepathfield_test_dir/c/e.py', 'e.py'),
        ('/filepathfield_test_dir/c/f/__init__.py', '__init__.py'),
        ('/filepathfield_test_dir/c/f/g.py', 'g.py'),
        ('/filepathfield_test_dir/h/__init__.py', '__init__.py'),
        ('/filepathfield_test_dir/j/__init__.py', '__init__.py'),
    ]
    path = os.path.join(PATH, 'filepathfield_test_dir') + '/'

    def assertChoices(self, field, expected_choices):
        self.assertEqual(fix_os_paths(field.choices), expected_choices)

    def test_fix_os_paths(self):
        self.assertEqual(fix_os_paths(self.path), ('/filepathfield_test_dir/'))

    def test_no_options(self):
        f = FilePathField(path=self.path)
        expected = [
            ('/filepathfield_test_dir/README', 'README'),
        ] + self.expected_choices[:4]
        self.assertChoices(f, expected)

    def test_clean(self):
        """
        Tests the clean method of the FilePathField.
        
        This method checks the validation and cleaning process of the FilePathField. It ensures that:
        1. An invalid file path raises a ValidationError with a specific message.
        2. A valid file path is correctly cleaned and normalized.
        
        Parameters:
        self: The instance of the test case class.
        
        Raises:
        ValidationError: If the input file path is invalid and does not match one of the available choices.
        
        Returns:
        str: The cleaned and normalized file path.
        """

        f = FilePathField(path=self.path)
        msg = "'Select a valid choice. a.py is not one of the available choices.'"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean('a.py')
        self.assertEqual(fix_os_paths(f.clean(self.path + 'a.py')), '/filepathfield_test_dir/a.py')

    def test_match(self):
        f = FilePathField(path=self.path, match=r'^.*?\.py$')
        self.assertChoices(f, self.expected_choices[:4])

    def test_recursive(self):
        """
        Tests the recursive functionality of FilePathField.
        
        This function checks if the FilePathField with the specified path and recursive flag set to True, along with a regex pattern to match Python files, correctly retrieves and returns a list of all Python files in the directory and its subdirectories. The expected output is a list of tuples, each containing the full path to a Python file and the file name.
        
        Parameters:
        None
        
        Returns:
        None
        
        Expected Output:
        A list of tuples, each containing the full
        """

        f = FilePathField(path=self.path, recursive=True, match=r'^.*?\.py$')
        expected = [
            ('/filepathfield_test_dir/__init__.py', '__init__.py'),
            ('/filepathfield_test_dir/a.py', 'a.py'),
            ('/filepathfield_test_dir/ab.py', 'ab.py'),
            ('/filepathfield_test_dir/b.py', 'b.py'),
            ('/filepathfield_test_dir/c/__init__.py', 'c/__init__.py'),
            ('/filepathfield_test_dir/c/d.py', 'c/d.py'),
            ('/filepathfield_test_dir/c/e.py', 'c/e.py'),
            ('/filepathfield_test_dir/c/f/__init__.py', 'c/f/__init__.py'),
            ('/filepathfield_test_dir/c/f/g.py', 'c/f/g.py'),
            ('/filepathfield_test_dir/h/__init__.py', 'h/__init__.py'),
            ('/filepathfield_test_dir/j/__init__.py', 'j/__init__.py'),

        ]
        self.assertChoices(f, expected)

    def test_allow_folders(self):
        f = FilePathField(path=self.path, allow_folders=True, allow_files=False)
        self.assertChoices(f, [
            ('/filepathfield_test_dir/c', 'c'),
            ('/filepathfield_test_dir/h', 'h'),
            ('/filepathfield_test_dir/j', 'j'),
        ])

    def test_recursive_no_folders_or_files(self):
        f = FilePathField(path=self.path, recursive=True, allow_folders=False, allow_files=False)
        self.assertChoices(f, [])

    def test_recursive_folders_without_files(self):
        """
        Tests the FilePathField with recursive=True, allow_folders=True, and allow_files=False.
        
        This function checks the FilePathField's behavior when set to recursively search for folders without allowing files. It ensures that only folder paths are included in the choices, and these paths are correctly displayed.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - path (str): The base path to start the recursive search from.
        - recursive (bool): Indicates if the search should be recursive.
        -
        """

        f = FilePathField(path=self.path, recursive=True, allow_folders=True, allow_files=False)
        self.assertChoices(f, [
            ('/filepathfield_test_dir/c', 'c'),
            ('/filepathfield_test_dir/h', 'h'),
            ('/filepathfield_test_dir/j', 'j'),
            ('/filepathfield_test_dir/c/f', 'c/f'),
        ])
