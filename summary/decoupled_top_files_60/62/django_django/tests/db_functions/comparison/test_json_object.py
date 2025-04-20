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
        Tests the functionality of the `JSONObject` annotation in Django ORM.
        
        This function creates an `Author` object and uses the `annotate` method to add a JSON object to the query result. The JSON object includes various fields derived from the model fields and constants. The function then asserts that the resulting JSON object matches the expected dictionary.
        
        Key Parameters:
        - `self`: The test case instance.
        
        Key Keyword Arguments:
        - `JSONObject`: Annotates the query result with a JSON object.
        - `name
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
        Tests the retrieval and annotation of a nested JSON object from an Author model instance.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Attributes:
        obj (Author): The first Author model instance from the database.
        
        Key Methods:
        json_object (JSONObject): Annotated JSON object containing nested attributes 'name' and 'nested_json_object'.
        - 'name': A string representing the author's name.
        - 'nested_json_object': Another JSONObject containing nested attributes 'alias' and 'age'.
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
        obj = Author.objects.annotate(json_object=JSONObject(
            name='name',
            nested_json_object=JSONObject(),
        )).first()
        self.assertEqual(obj.json_object, {
            'name': 'Ivan Ivanov',
            'nested_json_object': {},
        })

    def test_textfield(self):
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
        Tests the behavior of the JSONObject() function when used with the database backend.
        
        This function asserts that using JSONObject() to annotate a query results in a NotSupportedError, as the function is not supported by the current database backend.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        NotSupportedError: If JSONObject() is supported by the database backend.
        
        Usage:
        This function is used to verify that the JSONObject() function is correctly flagged as unsupported by the database backend in question.
        """

        msg = 'JSONObject() is not supported on this database backend.'
        with self.assertRaisesMessage(NotSupportedError, msg):
            Author.objects.annotate(json_object=JSONObject()).get()
