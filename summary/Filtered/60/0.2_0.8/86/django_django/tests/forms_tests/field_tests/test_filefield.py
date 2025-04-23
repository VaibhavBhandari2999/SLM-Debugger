import pickle

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import FileField
from django.test import SimpleTestCase


class FileFieldTest(SimpleTestCase):

    def test_filefield_1(self):
        """
        Tests for the FileField class.
        
        This function tests various scenarios for the FileField class, including:
        - Validation of empty strings and None values.
        - Handling of uploaded files.
        - Validation of non-file inputs.
        
        Parameters:
        - f: An instance of FileField to be tested.
        
        Returns:
        - None: The function asserts expected outcomes and does not return any value.
        
        Raises:
        - ValidationError: Raised when the input does not meet the expected criteria.
        
        Key Scenarios:
        1. Validation of empty strings and
        """

        f = FileField()
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean('')
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean('', '')
        self.assertEqual('files/test1.pdf', f.clean('', 'files/test1.pdf'))
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None)
        with self.assertRaisesMessage(ValidationError, "'This field is required.'"):
            f.clean(None, '')
        self.assertEqual('files/test2.pdf', f.clean(None, 'files/test2.pdf'))
        no_file_msg = "'No file was submitted. Check the encoding type on the form.'"
        file = SimpleUploadedFile(None, b'')
        file._name = ''
        with self.assertRaisesMessage(ValidationError, no_file_msg):
            f.clean(file)
        with self.assertRaisesMessage(ValidationError, no_file_msg):
            f.clean(file, '')
        self.assertEqual('files/test3.pdf', f.clean(None, 'files/test3.pdf'))
        with self.assertRaisesMessage(ValidationError, no_file_msg):
            f.clean('some content that is not a file')
        with self.assertRaisesMessage(ValidationError, "'The submitted file is empty.'"):
            f.clean(SimpleUploadedFile('name', None))
        with self.assertRaisesMessage(ValidationError, "'The submitted file is empty.'"):
            f.clean(SimpleUploadedFile('name', b''))
        self.assertEqual(SimpleUploadedFile, type(f.clean(SimpleUploadedFile('name', b'Some File Content'))))
        self.assertIsInstance(
            f.clean(SimpleUploadedFile('我隻氣墊船裝滿晒鱔.txt', 'मेरी मँडराने वाली नाव सर्पमीनों से भरी ह'.encode())),
            SimpleUploadedFile
        )
        self.assertIsInstance(
            f.clean(SimpleUploadedFile('name', b'Some File Content'), 'files/test4.pdf'),
            SimpleUploadedFile
        )

    def test_filefield_2(self):
        """
        Tests for the FileField class.
        
        This function tests the validation and cleaning behavior of the FileField class.
        
        Parameters:
        f (FileField): The FileField instance to test.
        
        Key Parameters:
        - max_length (int): The maximum allowed length of the filename.
        
        Input:
        - A FileField instance with a specified max_length.
        - A SimpleUploadedFile object with a filename and content.
        
        Output:
        - Raises a ValidationError if the filename exceeds the max_length.
        - Returns the
        """

        f = FileField(max_length=5)
        with self.assertRaisesMessage(ValidationError, "'Ensure this filename has at most 5 characters (it has 18).'"):
            f.clean(SimpleUploadedFile('test_maxlength.txt', b'hello world'))
        self.assertEqual('files/test1.pdf', f.clean('', 'files/test1.pdf'))
        self.assertEqual('files/test2.pdf', f.clean(None, 'files/test2.pdf'))
        self.assertIsInstance(f.clean(SimpleUploadedFile('name', b'Some File Content')), SimpleUploadedFile)

    def test_filefield_3(self):
        f = FileField(allow_empty_file=True)
        self.assertIsInstance(f.clean(SimpleUploadedFile('name', b'')), SimpleUploadedFile)

    def test_filefield_changed(self):
        """
        The value of data will more than likely come from request.FILES. The
        value of initial data will likely be a filename stored in the database.
        Since its value is of no use to a FileField it is ignored.
        """
        f = FileField()

        # No file was uploaded and no initial data.
        self.assertFalse(f.has_changed('', None))

        # A file was uploaded and no initial data.
        self.assertTrue(f.has_changed('', {'filename': 'resume.txt', 'content': 'My resume'}))

        # A file was not uploaded, but there is initial data
        self.assertFalse(f.has_changed('resume.txt', None))

        # A file was uploaded and there is initial data (file identity is not dealt
        # with here)
        self.assertTrue(f.has_changed('resume.txt', {'filename': 'resume.txt', 'content': 'My resume'}))

    def test_disabled_has_changed(self):
        f = FileField(disabled=True)
        self.assertIs(f.has_changed('x', 'y'), False)

    def test_file_picklable(self):
        self.assertIsInstance(pickle.loads(pickle.dumps(FileField())), FileField)
