"""
This Python file contains unit tests for the `JSONObject` function in Django. The `JSONObjectTests` class includes several test methods to validate different aspects of the `JSONObject` function, such as creating basic JSON objects, handling expressions, and dealing with nested JSON objects. The `JSONObjectNotSupportedTests` class ensures that the `JSONObject` function is correctly flagged as unsupported when the database backend does not support it. The tests use Django's ORM to manipulate and query models (`Author` and `Article`) and assert the correctness of the generated JSON objects. ```python
"""
from django.db import NotSupportedError
from django.db.models import F, Value
from django.db.models.functions import JSONObject, Lower
from django.test import TestCase
from django.test.testcases import skipIfDBFeature, skipUnlessDBFeature
from django.utils import timezone

from ..models import Article, Author


@skipUnlessDBFeature('has_json_object_function')
class JSONObjectTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Author.objects.create(name='Ivan Ivanov', alias='iivanov')

    def test_empty(self):
        obj = Author.objects.annotate(json_object=JSONObject()).first()
        self.assertEqual(obj.json_object, {})

    def test_basic(self):
        obj = Author.objects.annotate(json_object=JSONObject(name='name')).first()
        self.assertEqual(obj.json_object, {'name': 'Ivan Ivanov'})

    def test_expressions(self):
        """
        Tests the functionality of the `JSONObject` annotation in Django queries.
        It creates an `Author` object with specific annotations that transform various fields into a JSON object.
        The `Lower`, `Value`, `F`, and `JSONObject` functions are used to manipulate the fields.
        The resulting JSON object is then compared to an expected dictionary to verify correctness.
        """

        obj = Author.objects.annotate(json_object=JSONObject(
            name=Lower('name'),
            alias='alias',
            goes_by='goes_by',
            salary=Value(30000.15),
            age=F('age') * 2,
        )).first()
        self.assertEqual(obj.json_object, {
            'name': 'ivan ivanov',
            'alias': 'iivanov',
            'goes_by': None,
            'salary': 30000.15,
            'age': 60,
        })

    def test_nested_json_object(self):
        """
        Tests the functionality of the `JSONObject` annotation in the `Author` model.
        It creates an `Author` object with annotated JSON fields: 'name' and 'nested_json_object' containing 'alias' and 'age'.
        The expected output is a dictionary with the specified key-value pairs.
        """

        obj = Author.objects.annotate(json_object=JSONObject(
            name='name',
            nested_json_object=JSONObject(
                alias='alias',
                age='age',
            ),
        )).first()
        self.assertEqual(obj.json_object, {
            'name': 'Ivan Ivanov',
            'nested_json_object': {
                'alias': 'iivanov',
                'age': 30,
            },
        })

    def test_nested_empty_json_object(self):
        """
        Tests the behavior of annotating an Author object with a nested empty JSON object using the JSONObject function.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the annotated JSON object does not match the expected output.
        
        Important Functions:
        - `JSONObject`: Used to create a nested JSON object.
        - `Author.objects.annotate()`: Annotates the Author model queryset with the specified JSON object.
        
        Expected Output:
        The annotated JSON object should have the
        """

        obj = Author.objects.annotate(json_object=JSONObject(
            name='name',
            nested_json_object=JSONObject(),
        )).first()
        self.assertEqual(obj.json_object, {
            'name': 'Ivan Ivanov',
            'nested_json_object': {},
        })

    def test_textfield(self):
        """
        Tests the functionality of the `test_textfield` method.
        
        This method creates an instance of the `Article` model with a long text field and then uses the `annotate` method along with `JSONObject` and `F` expressions to create a JSON object representation of the text field. The expected result is that the JSON object contains the key 'text' with the value equal to the original text field value.
        """

        Article.objects.create(
            title='The Title',
            text='x' * 4000,
            written=timezone.now(),
        )
        obj = Article.objects.annotate(json_object=JSONObject(text=F('text'))).first()
        self.assertEqual(obj.json_object, {'text': 'x' * 4000})


@skipIfDBFeature('has_json_object_function')
class JSONObjectNotSupportedTests(TestCase):
    def test_not_supported(self):
        """
        Test that the JSONObject() function is not supported on the current database backend.
        
        Summary: This function tests whether the JSONObject() function is supported by the current database backend. If not supported, it raises a NotSupportedError with a specific message. The function uses the `annotate` method of the Author model's queryset to attempt using JSONObject(), and then calls `get()` to trigger the error if JSONObject() is not supported.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        """

        msg = 'JSONObject() is not supported on this database backend.'
        with self.assertRaisesMessage(NotSupportedError, msg):
            Author.objects.annotate(json_object=JSONObject()).get()
