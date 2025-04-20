from io import BytesIO

from django.core.exceptions import RequestDataTooBig, TooManyFieldsSent
from django.core.handlers.wsgi import WSGIRequest
from django.test import SimpleTestCase
from django.test.client import FakePayload

TOO_MANY_FIELDS_MSG = 'The number of GET/POST parameters exceeded settings.DATA_UPLOAD_MAX_NUMBER_FIELDS.'
TOO_MUCH_DATA_MSG = 'Request body exceeded settings.DATA_UPLOAD_MAX_MEMORY_SIZE.'


class DataUploadMaxMemorySizeFormPostTests(SimpleTestCase):
    def setUp(self):
        """
        Sets up a test request for processing.
        
        This method initializes a test request object with specific attributes and a payload. The request is configured to handle a POST method with a content type of 'application/x-www-form-urlencoded'. The payload contains form data with multiple values for the same key.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Attributes:
        - request (WSGIRequest): The test request object configured with the specified attributes.
        - payload (FakePayload): The form data payload used for
        """

        payload = FakePayload('a=1&a=2;a=3\r\n')
        self.request = WSGIRequest({
            'REQUEST_METHOD': 'POST',
            'CONTENT_TYPE': 'application/x-www-form-urlencoded',
            'CONTENT_LENGTH': len(payload),
            'wsgi.input': payload,
        })

    def test_size_exceeded(self):
        with self.settings(DATA_UPLOAD_MAX_MEMORY_SIZE=12):
            with self.assertRaisesMessage(RequestDataTooBig, TOO_MUCH_DATA_MSG):
                self.request._load_post_and_files()

    def test_size_not_exceeded(self):
        with self.settings(DATA_UPLOAD_MAX_MEMORY_SIZE=13):
            self.request._load_post_and_files()

    def test_no_limit(self):
        with self.settings(DATA_UPLOAD_MAX_MEMORY_SIZE=None):
            self.request._load_post_and_files()


class DataUploadMaxMemorySizeMultipartPostTests(SimpleTestCase):
    def setUp(self):
        """
        Sets up a test request for handling multipart form data.
        
        This method prepares a test request object with a POST method and a multipart form data payload. The payload consists of a single form field named 'name' with the value 'value'. The request is configured with the appropriate content type and length headers.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Attributes:
        - request (WSGIRequest): The test request object configured with the multipart form data payload.
        
        Notes:
        - The payload is
        """

        payload = FakePayload("\r\n".join([
            '--boundary',
            'Content-Disposition: form-data; name="name"',
            '',
            'value',
            '--boundary--'
            ''
        ]))
        self.request = WSGIRequest({
            'REQUEST_METHOD': 'POST',
            'CONTENT_TYPE': 'multipart/form-data; boundary=boundary',
            'CONTENT_LENGTH': len(payload),
            'wsgi.input': payload,
        })

    def test_size_exceeded(self):
        with self.settings(DATA_UPLOAD_MAX_MEMORY_SIZE=10):
            with self.assertRaisesMessage(RequestDataTooBig, TOO_MUCH_DATA_MSG):
                self.request._load_post_and_files()

    def test_size_not_exceeded(self):
        with self.settings(DATA_UPLOAD_MAX_MEMORY_SIZE=11):
            self.request._load_post_and_files()

    def test_no_limit(self):
        with self.settings(DATA_UPLOAD_MAX_MEMORY_SIZE=None):
            self.request._load_post_and_files()

    def test_file_passes(self):
        """
        Tests if a file is correctly passed in a multipart form data POST request.
        
        This function checks if a file named 'test.file' with the content 'value' is correctly uploaded in a multipart form data POST request. The test is performed with a maximum memory size of 1 byte for the uploaded file.
        
        Parameters:
        - None (The function uses internal settings and variables)
        
        Returns:
        - None (The function asserts the presence of the uploaded file in the request.FILES dictionary)
        
        Key Parameters:
        - None
        """

        payload = FakePayload("\r\n".join([
            '--boundary',
            'Content-Disposition: form-data; name="file1"; filename="test.file"',
            '',
            'value',
            '--boundary--'
            ''
        ]))
        request = WSGIRequest({
            'REQUEST_METHOD': 'POST',
            'CONTENT_TYPE': 'multipart/form-data; boundary=boundary',
            'CONTENT_LENGTH': len(payload),
            'wsgi.input': payload,
        })
        with self.settings(DATA_UPLOAD_MAX_MEMORY_SIZE=1):
            request._load_post_and_files()
            self.assertIn('file1', request.FILES, "Upload file not present")


class DataUploadMaxMemorySizeGetTests(SimpleTestCase):
    def setUp(self):
        self.request = WSGIRequest({
            'REQUEST_METHOD': 'GET',
            'wsgi.input': BytesIO(b''),
            'CONTENT_LENGTH': 3,
        })

    def test_data_upload_max_memory_size_exceeded(self):
        with self.settings(DATA_UPLOAD_MAX_MEMORY_SIZE=2):
            with self.assertRaisesMessage(RequestDataTooBig, TOO_MUCH_DATA_MSG):
                self.request.body

    def test_size_not_exceeded(self):
        with self.settings(DATA_UPLOAD_MAX_MEMORY_SIZE=3):
            self.request.body

    def test_no_limit(self):
        with self.settings(DATA_UPLOAD_MAX_MEMORY_SIZE=None):
            self.request.body

    def test_empty_content_length(self):
        self.request.environ['CONTENT_LENGTH'] = ''
        self.request.body


class DataUploadMaxNumberOfFieldsGet(SimpleTestCase):

    def test_get_max_fields_exceeded(self):
        with self.settings(DATA_UPLOAD_MAX_NUMBER_FIELDS=1):
            with self.assertRaisesMessage(TooManyFieldsSent, TOO_MANY_FIELDS_MSG):
                request = WSGIRequest({
                    'REQUEST_METHOD': 'GET',
                    'wsgi.input': BytesIO(b''),
                    'QUERY_STRING': 'a=1&a=2;a=3',
                })
                request.GET['a']

    def test_get_max_fields_not_exceeded(self):
        with self.settings(DATA_UPLOAD_MAX_NUMBER_FIELDS=3):
            request = WSGIRequest({
                'REQUEST_METHOD': 'GET',
                'wsgi.input': BytesIO(b''),
                'QUERY_STRING': 'a=1&a=2;a=3',
            })
            request.GET['a']


class DataUploadMaxNumberOfFieldsMultipartPost(SimpleTestCase):
    def setUp(self):
        payload = FakePayload("\r\n".join([
            '--boundary',
            'Content-Disposition: form-data; name="name1"',
            '',
            'value1',
            '--boundary',
            'Content-Disposition: form-data; name="name2"',
            '',
            'value2',
            '--boundary--'
            ''
        ]))
        self.request = WSGIRequest({
            'REQUEST_METHOD': 'POST',
            'CONTENT_TYPE': 'multipart/form-data; boundary=boundary',
            'CONTENT_LENGTH': len(payload),
            'wsgi.input': payload,
        })

    def test_number_exceeded(self):
        """
        Tests the behavior when the number of fields in the request exceeds the maximum allowed.
        
        This function checks if the request contains more fields than the specified maximum number of fields. If the number of fields exceeds the limit, a `TooManyFieldsSent` exception is raised with a specific message.
        
        Key Parameters:
        - None
        
        Keywords:
        - None
        
        Inputs:
        - None (uses `self.settings` and `self.request` from the test environment)
        
        Outputs:
        - Raises `TooManyFieldsSent` exception with
        """

        with self.settings(DATA_UPLOAD_MAX_NUMBER_FIELDS=1):
            with self.assertRaisesMessage(TooManyFieldsSent, TOO_MANY_FIELDS_MSG):
                self.request._load_post_and_files()

    def test_number_not_exceeded(self):
        with self.settings(DATA_UPLOAD_MAX_NUMBER_FIELDS=2):
            self.request._load_post_and_files()

    def test_no_limit(self):
        with self.settings(DATA_UPLOAD_MAX_NUMBER_FIELDS=None):
            self.request._load_post_and_files()


class DataUploadMaxNumberOfFieldsFormPost(SimpleTestCase):
    def setUp(self):
        payload = FakePayload("\r\n".join(['a=1&a=2;a=3', '']))
        self.request = WSGIRequest({
            'REQUEST_METHOD': 'POST',
            'CONTENT_TYPE': 'application/x-www-form-urlencoded',
            'CONTENT_LENGTH': len(payload),
            'wsgi.input': payload,
        })

    def test_number_exceeded(self):
        with self.settings(DATA_UPLOAD_MAX_NUMBER_FIELDS=2):
            with self.assertRaisesMessage(TooManyFieldsSent, TOO_MANY_FIELDS_MSG):
                self.request._load_post_and_files()

    def test_number_not_exceeded(self):
        with self.settings(DATA_UPLOAD_MAX_NUMBER_FIELDS=3):
            self.request._load_post_and_files()

    def test_no_limit(self):
        with self.settings(DATA_UPLOAD_MAX_NUMBER_FIELDS=None):
            self.request._load_post_and_files()
