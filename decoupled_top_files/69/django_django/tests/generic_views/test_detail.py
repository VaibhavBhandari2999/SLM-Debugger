"""
This Python file contains unit tests for various detail views in a Django application. It primarily focuses on testing different ways to retrieve and display objects from the database, including by primary key, slug, and custom identifiers. The tests cover scenarios such as successful retrieval, handling of missing or invalid objects, and ensuring proper context and templates are used. The file also includes tests for custom detail views and mixins, such as handling deferred querysets and context object names. The setup method initializes test data for the models used in the tests. The tests utilize Django's `TestCase` and `RequestFactory` to simulate HTTP requests and verify the behavior of the views. ### Docstring

```python
"""
import datetime

from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.test import TestCase, override_settings
from django.test.client import RequestFactory
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.edit import ModelFormMixin

from .models import Artist, Author, Book, Page


@override_settings(ROOT_URLCONF='generic_views.urls')
class DetailViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for the tests in this class.
        
        This method creates instances of `Artist`, `Author`, `Book`, and `Page` models and adds relationships between them. Specifically, it:
        
        - Creates an `Artist` instance named 'Rene Magritte'.
        - Creates two `Author` instances: 'Roberto Bolaño' and 'Scott Rosenberg'.
        - Creates a `Book` instance named '2066' with 800 pages published on
        """

        cls.artist1 = Artist.objects.create(name='Rene Magritte')
        cls.author1 = Author.objects.create(name='Roberto Bolaño', slug='roberto-bolano')
        cls.author2 = Author.objects.create(name='Scott Rosenberg', slug='scott-rosenberg')
        cls.book1 = Book.objects.create(name='2066', slug='2066', pages=800, pubdate=datetime.date(2008, 10, 1))
        cls.book1.authors.add(cls.author1)
        cls.book2 = Book.objects.create(
            name='Dreaming in Code', slug='dreaming-in-code', pages=300, pubdate=datetime.date(2006, 5, 1)
        )
        cls.page1 = Page.objects.create(
            content='I was once bitten by a moose.', template='generic_views/page_template.html'
        )

    def test_simple_object(self):
        """
        Tests the behavior of the `test_simple_object` method. It sends a GET request to '/detail/obj/', checks if the response status code is 200, verifies that the context contains an object with the key 'foo' and value 'bar', ensures that the context includes an instance of the 'View' class, and confirms that the correct template ('generic_views/detail.html') was used.
        """

        res = self.client.get('/detail/obj/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], {'foo': 'bar'})
        self.assertIsInstance(res.context['view'], View)
        self.assertTemplateUsed(res, 'generic_views/detail.html')

    def test_detail_by_pk(self):
        """
        Tests the detail view for an author by primary key (pk).
        
        This function sends a GET request to the '/detail/author/<pk>/' URL with the primary key of `self.author1` and checks if the response status code is 200, the context contains the correct author object, and the correct template is used.
        
        Args:
        None
        
        Returns:
        None
        """

        res = self.client.get('/detail/author/%s/' % self.author1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], self.author1)
        self.assertEqual(res.context['author'], self.author1)
        self.assertTemplateUsed(res, 'generic_views/author_detail.html')

    def test_detail_missing_object(self):
        res = self.client.get('/detail/author/500/')
        self.assertEqual(res.status_code, 404)

    def test_detail_object_does_not_exist(self):
        with self.assertRaises(ObjectDoesNotExist):
            self.client.get('/detail/doesnotexist/1/')

    def test_detail_by_custom_pk(self):
        """
        Tests the detail view for an author using a custom primary key. Sends a GET request to '/detail/author/bycustompk/<author_pk>/'. Verifies that the response status code is 200, the context contains the correct author object, and the appropriate template is used.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `client.get()`: Sends a GET request to the specified URL.
        - `assertEqual()`: Compares the
        """

        res = self.client.get('/detail/author/bycustompk/%s/' % self.author1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], self.author1)
        self.assertEqual(res.context['author'], self.author1)
        self.assertTemplateUsed(res, 'generic_views/author_detail.html')

    def test_detail_by_slug(self):
        """
        Tests the detail view for an author by slug.
        
        This function sends a GET request to the '/detail/author/byslug/scott-rosenberg/' URL and checks if the response status code is 200, the context contains the correct author object, and the correct template is used.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `client.get()`: Sends a GET request to the specified URL.
        - `Author.objects.get()
        """

        res = self.client.get('/detail/author/byslug/scott-rosenberg/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], Author.objects.get(slug='scott-rosenberg'))
        self.assertEqual(res.context['author'], Author.objects.get(slug='scott-rosenberg'))
        self.assertTemplateUsed(res, 'generic_views/author_detail.html')

    def test_detail_by_custom_slug(self):
        """
        Tests the detail view for an author with a custom slug. Sends a GET request to '/detail/author/bycustomslug/scott-rosenberg/' and checks that the response status code is 200, the context contains the correct author object, and the correct template is used.
        """

        res = self.client.get('/detail/author/bycustomslug/scott-rosenberg/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], Author.objects.get(slug='scott-rosenberg'))
        self.assertEqual(res.context['author'], Author.objects.get(slug='scott-rosenberg'))
        self.assertTemplateUsed(res, 'generic_views/author_detail.html')

    def test_detail_by_pk_ignore_slug(self):
        """
        Tests the detail view for an author by primary key while ignoring the slug.
        
        This function sends a GET request to the '/detail/author/bypkignoreslug/<pk>-roberto-bolano/' URL with the primary key of the author1 object. It then checks if the response status code is 200 (indicating success), if the context contains the correct author object, and if the correct template is used.
        
        :param: None
        :return:
        """

        res = self.client.get('/detail/author/bypkignoreslug/%s-roberto-bolano/' % self.author1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], self.author1)
        self.assertEqual(res.context['author'], self.author1)
        self.assertTemplateUsed(res, 'generic_views/author_detail.html')

    def test_detail_by_pk_ignore_slug_mismatch(self):
        """
        Tests the detail view by primary key with slug mismatch.
        
        This function sends a GET request to the '/detail/author/bypkignoreslug/<pk>-<slug>/' URL using the client and verifies that the response status code is 200, the context contains the correct author object, and the appropriate template is used.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `client.get()`: Sends a GET request to the specified URL
        """

        res = self.client.get('/detail/author/bypkignoreslug/%s-scott-rosenberg/' % self.author1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], self.author1)
        self.assertEqual(res.context['author'], self.author1)
        self.assertTemplateUsed(res, 'generic_views/author_detail.html')

    def test_detail_by_pk_and_slug(self):
        """
        Tests the detail view for an author by primary key and slug.
        
        This function sends a GET request to the '/detail/author/bypkandslug/<pk>-<slug>/'
        URL with the primary key of an author and their slug. It then checks if the response
        status code is 200 (OK), if the context contains the correct author object, and if
        the correct template is used.
        
        Args:
        None
        
        Returns:
        None
        """

        res = self.client.get('/detail/author/bypkandslug/%s-roberto-bolano/' % self.author1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], self.author1)
        self.assertEqual(res.context['author'], self.author1)
        self.assertTemplateUsed(res, 'generic_views/author_detail.html')

    def test_detail_by_pk_and_slug_mismatch_404(self):
        res = self.client.get('/detail/author/bypkandslug/%s-scott-rosenberg/' % self.author1.pk)
        self.assertEqual(res.status_code, 404)

    def test_verbose_name(self):
        """
        Tests the artist detail view with verbose name. Verifies that the response status code is 200, the context contains the correct artist object, and the correct template is used.
        """

        res = self.client.get('/detail/artist/%s/' % self.artist1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], self.artist1)
        self.assertEqual(res.context['artist'], self.artist1)
        self.assertTemplateUsed(res, 'generic_views/artist_detail.html')

    def test_template_name(self):
        """
        Tests the template name used in the detail view for an author.
        
        Args:
        self: The current instance of the test class.
        
        Returns:
        None
        
        Effects:
        - Sends a GET request to '/detail/author/<author_id>/template_name/'.
        - Asserts that the response status code is 200 (OK).
        - Asserts that the context contains the correct author object.
        - Asserts that the correct template ('generic_views/about.html') is
        """

        res = self.client.get('/detail/author/%s/template_name/' % self.author1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], self.author1)
        self.assertEqual(res.context['author'], self.author1)
        self.assertTemplateUsed(res, 'generic_views/about.html')

    def test_template_name_suffix(self):
        """
        Tests the template name suffix functionality by making a GET request to the author detail view with a specific author's primary key and verifying the response status code, context data, and template used.
        """

        res = self.client.get('/detail/author/%s/template_name_suffix/' % self.author1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], self.author1)
        self.assertEqual(res.context['author'], self.author1)
        self.assertTemplateUsed(res, 'generic_views/author_view.html')

    def test_template_name_field(self):
        """
        Tests the template name field functionality for a page detail view. Sends a GET request to '/detail/page/<page_id>/field/' and checks that the response status code is 200, the context contains the correct page object, the template used is 'generic_views/page_template.html', and the context variable 'page' matches the 'object' variable.
        """

        res = self.client.get('/detail/page/%s/field/' % self.page1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], self.page1)
        self.assertEqual(res.context['page'], self.page1)
        self.assertTemplateUsed(res, 'generic_views/page_template.html')

    def test_context_object_name(self):
        """
        Tests the context object name functionality of a view. The view is expected to use the 'author_detail' template and return a HTTP 200 response. The context should contain 'object' and 'thingy' keys with values set to the author instance, and should not contain a 'author' key.
        """

        res = self.client.get('/detail/author/%s/context_object_name/' % self.author1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], self.author1)
        self.assertEqual(res.context['thingy'], self.author1)
        self.assertNotIn('author', res.context)
        self.assertTemplateUsed(res, 'generic_views/author_detail.html')

    def test_duplicated_context_object_name(self):
        """
        Tests the behavior of a view when a context object name is duplicated. The function sends a GET request to '/detail/author/<author_id>/dupe_context_object_name/' with the author's primary key, expecting a 200 status code. It then checks that the context contains an object with the same primary key as the author, does not contain a variable named 'author', and uses the specified template. The function uses client.get(), assertEqual(), assertNotIn(), and assertTemplate
        """

        res = self.client.get('/detail/author/%s/dupe_context_object_name/' % self.author1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], self.author1)
        self.assertNotIn('author', res.context)
        self.assertTemplateUsed(res, 'generic_views/author_detail.html')

    def test_custom_detail(self):
        """
        AuthorCustomDetail overrides get() and ensures that
        SingleObjectMixin.get_context_object_name() always uses the obj
        parameter instead of self.object.
        """
        res = self.client.get('/detail/author/%s/custom_detail/' % self.author1.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['custom_author'], self.author1)
        self.assertNotIn('author', res.context)
        self.assertNotIn('object', res.context)
        self.assertTemplateUsed(res, 'generic_views/author_detail.html')

    def test_deferred_queryset_template_name(self):
        """
        Tests the deferred queryset template name functionality using SingleObjectTemplateResponseMixin. Creates an instance of FormContext with a deferred queryset and verifies that the correct template name is returned.
        """

        class FormContext(SingleObjectTemplateResponseMixin):
            request = RequestFactory().get('/')
            model = Author
            object = Author.objects.defer('name').get(pk=self.author1.pk)

        self.assertEqual(FormContext().get_template_names()[0], 'generic_views/author_detail.html')

    def test_deferred_queryset_context_object_name(self):
        """
        Tests the deferred queryset context object name functionality of ModelFormMixin.
        
        This function creates an instance of `FormContext` which is a subclass of `ModelFormMixin`. It sets up a GET request, defines the model as `Author`, and retrieves an author object with a deferred 'name' field. The `get_context_data` method is called to generate context data. The function asserts that the context data contains both 'object' and 'author' keys, pointing to the same `Author`
        """

        class FormContext(ModelFormMixin):
            request = RequestFactory().get('/')
            model = Author
            object = Author.objects.defer('name').get(pk=self.author1.pk)
            fields = ('name',)

        form_context_data = FormContext().get_context_data()
        self.assertEqual(form_context_data['object'], self.author1)
        self.assertEqual(form_context_data['author'], self.author1)

    def test_invalid_url(self):
        with self.assertRaises(AttributeError):
            self.client.get('/detail/author/invalid/url/')

    def test_invalid_queryset(self):
        """
        Tests that an ImproperlyConfigured exception is raised when AuthorDetail view is missing a QuerySet. The function checks if AuthorDetail has a defined model, queryset, or get_queryset method. If none of these are defined, it raises an ImproperlyConfigured exception with a specific message.
        """

        msg = (
            'AuthorDetail is missing a QuerySet. Define AuthorDetail.model, '
            'AuthorDetail.queryset, or override AuthorDetail.get_queryset().'
        )
        with self.assertRaisesMessage(ImproperlyConfigured, msg):
            self.client.get('/detail/author/invalid/qs/')

    def test_non_model_object_with_meta(self):
        """
        Tests the behavior of retrieving a non-model object with a custom meta class using the client's GET request.
        
        Summary:
        - Uses Django's test client to send a GET request to '/detail/nonmodel/1/'.
        - Asserts that the response status code is 200 (OK).
        - Asserts that the 'object' in the context has an 'id' attribute equal to 'non_model_1'.
        """

        res = self.client.get('/detail/nonmodel/1/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'].id, "non_model_1")
