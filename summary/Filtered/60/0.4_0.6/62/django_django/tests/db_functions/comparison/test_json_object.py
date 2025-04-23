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
        
        This function creates an `Author` object and uses the `JSONObject` annotation to generate a nested JSON object. The `JSONObject` is used to create a nested structure with the fields 'name', 'alias', and 'age'. The function asserts that the generated JSON object matches the expected structure.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Assertions:
        - The `json_object` attribute of the first `Author`
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
        """
        Tests the functionality of the textfield in the Article model.
        
        This function creates an instance of the Article model with a long text field and then uses the JSONObject function to annotate the query with a JSON object containing the text field. The test asserts that the annotated JSON object matches the original text field content.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Parameters:
        - None
        
        Key Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - None
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
        msg = 'JSONObject() is not supported on this database backend.'
        with self.assertRaisesMessage(NotSupportedError, msg):
            Author.objects.annotate(json_object=JSONObject()).get()
