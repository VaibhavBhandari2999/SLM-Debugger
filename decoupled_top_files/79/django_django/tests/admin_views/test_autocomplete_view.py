"""
This Python file contains unit tests and configurations for an autocomplete feature in a Django admin interface. It includes:

- **Classes and Functions**:
  - `AuthorAdmin`: A custom ModelAdmin for the `Author` model.
  - `BookAdmin`: A custom ModelAdmin for the `Book` model.
  - `model_admin`: A context manager for registering and unregistering Django model admin configurations.
  - `AutocompleteJsonViewTests`: A test class for the `AutocompleteJsonView` view, which handles AJAX requests for autocompletion.
  - `SeleniumTests`: A Selenium test class for testing the autocomplete functionality in a browser environment.

- **Key Responsibilities**:
  - The `AuthorAdmin` and `BookAdmin
"""
import json
from contextlib import contextmanager

from django.contrib import admin
from django.contrib.admin.tests import AdminSeleniumTestCase
from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.test import RequestFactory, override_settings
from django.urls import reverse, reverse_lazy

from .admin import AnswerAdmin, QuestionAdmin
from .models import (
    Answer, Author, Authorship, Bonus, Book, Employee, Manager, Parent,
    PKChild, Question, Toy, WorkHour,
)
from .tests import AdminViewBasicTestCase

PAGINATOR_SIZE = AutocompleteJsonView.paginate_by


class AuthorAdmin(admin.ModelAdmin):
    ordering = ['id']
    search_fields = ['id']


class AuthorshipInline(admin.TabularInline):
    model = Authorship
    autocomplete_fields = ['author']


class BookAdmin(admin.ModelAdmin):
    inlines = [AuthorshipInline]


site = admin.AdminSite(name='autocomplete_admin')
site.register(Question, QuestionAdmin)
site.register(Answer, AnswerAdmin)
site.register(Author, AuthorAdmin)
site.register(Book, BookAdmin)
site.register(Employee, search_fields=['name'])
site.register(WorkHour, autocomplete_fields=['employee'])
site.register(Manager, search_fields=['name'])
site.register(Bonus, autocomplete_fields=['recipient'])
site.register(PKChild, search_fields=['name'])
site.register(Toy, autocomplete_fields=['child'])


@contextmanager
def model_admin(model, model_admin, admin_site=site):
    """
    Registers a Django model with a custom ModelAdmin instance, optionally unregistering the original admin configuration. Yields control to the caller, and re-registers the original admin configuration upon completion.
    
    Args:
    model (Model): The Django model to be registered.
    model_admin (ModelAdmin): The custom ModelAdmin instance to use for the model.
    admin_site (Site, optional): The Django admin site to register the model with. Defaults to `site`.
    
    Returns:
    None: This
    """

    org_admin = admin_site._registry.get(model)
    if org_admin:
        admin_site.unregister(model)
    admin_site.register(model, model_admin)
    try:
        yield
    finally:
        if org_admin:
            admin_site._registry[model] = org_admin


class AutocompleteJsonViewTests(AdminViewBasicTestCase):
    as_view_args = {'admin_site': site}
    opts = {
        'app_label': Answer._meta.app_label,
        'model_name': Answer._meta.model_name,
        'field_name': 'question'
    }
    factory = RequestFactory()
    url = reverse_lazy('autocomplete_admin:autocomplete')

    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for a class-based view.
        
        This method creates a test user with the following attributes:
        - Username: 'user'
        - Password: 'secret'
        - Email: 'user@example.com'
        - Is staff: True
        
        It then calls the superclass's `setUpTestData` method to further set up any additional test data required by the parent class.
        
        Args:
        cls (cls): The class object on which this method is being called.
        
        Returns:
        """

        cls.user = User.objects.create_user(
            username='user', password='secret',
            email='user@example.com', is_staff=True,
        )
        super().setUpTestData()

    def test_success(self):
        """
        Tests the success scenario of the AutocompleteJsonView.
        
        This function creates a question object, makes a GET request with specific parameters, and verifies the response from the view. It checks that the status code is 200 and that the returned JSON contains the expected question data.
        
        :param self: The current instance of the test class.
        :type self: unittest.TestCase
        
        :ivar q: The created question object.
        :vartype q: Question
        
        :ivar
        """

        q = Question.objects.create(question='Is this a question?')
        request = self.factory.get(self.url, {'term': 'is', **self.opts})
        request.user = self.superuser
        response = AutocompleteJsonView.as_view(**self.as_view_args)(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, {
            'results': [{'id': str(q.pk), 'text': q.question}],
            'pagination': {'more': False},
        })

    def test_custom_to_field(self):
        """
        Tests the custom `to_field` functionality of the AutocompleteJsonView.
        
        This function sends a GET request to the specified URL with a term 'is' and a field name 'question_with_to_field'.
        It then checks if the response status code is 200 and if the returned JSON data matches the expected format,
        which includes the question's UUID and text.
        """

        q = Question.objects.create(question='Is this a question?')
        request = self.factory.get(self.url, {'term': 'is', **self.opts, 'field_name': 'question_with_to_field'})
        request.user = self.superuser
        response = AutocompleteJsonView.as_view(**self.as_view_args)(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, {
            'results': [{'id': str(q.uuid), 'text': q.question}],
            'pagination': {'more': False},
        })

    def test_custom_to_field_permission_denied(self):
        """
        Raises PermissionDenied when attempting to access an autocomplete view for a model field with a custom to_field, ensuring that only authorized users can perform such actions.
        
        Args:
        request (HttpRequest): The HTTP GET request containing the search term and field name.
        
        Raises:
        PermissionDenied: If the user is not authorized to access the specified field with a custom to_field.
        
        Important Functions:
        - `Question.objects.create`: Creates a new instance of the Question model.
        - `request.user`:
        """

        Question.objects.create(question='Is this a question?')
        request = self.factory.get(self.url, {'term': 'is', **self.opts, 'field_name': 'question_with_to_field'})
        request.user = self.user
        with self.assertRaises(PermissionDenied):
            AutocompleteJsonView.as_view(**self.as_view_args)(request)

    def test_custom_to_field_custom_pk(self):
        """
        Tests the custom `to_field` parameter with a custom primary key.
        
        This function creates a `Question` object, constructs a request with specific parameters including the app label, model name, field name, and term, and sends it to the `AutocompleteJsonView`. It then checks if the response status code is 200 and if the returned JSON contains the expected results, specifically the ID and text of the created `Question` object.
        """

        q = Question.objects.create(question='Is this a question?')
        opts = {
            'app_label': Question._meta.app_label,
            'model_name': Question._meta.model_name,
            'field_name': 'related_questions',
        }
        request = self.factory.get(self.url, {'term': 'is', **opts})
        request.user = self.superuser
        response = AutocompleteJsonView.as_view(**self.as_view_args)(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, {
            'results': [{'id': str(q.big_id), 'text': q.question}],
            'pagination': {'more': False},
        })

    def test_to_field_resolution_with_mti(self):
        """
        to_field resolution should correctly resolve for target models using
        MTI. Tests for single and multi-level cases.
        """
        tests = [
            (Employee, WorkHour, 'employee'),
            (Manager, Bonus, 'recipient'),
        ]
        for Target, Remote, related_name in tests:
            with self.subTest(target_model=Target, remote_model=Remote, related_name=related_name):
                o = Target.objects.create(name="Frida Kahlo", gender=2, code="painter", alive=False)
                opts = {
                    'app_label': Remote._meta.app_label,
                    'model_name': Remote._meta.model_name,
                    'field_name': related_name,
                }
                request = self.factory.get(self.url, {'term': 'frida', **opts})
                request.user = self.superuser
                response = AutocompleteJsonView.as_view(**self.as_view_args)(request)
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.content.decode('utf-8'))
                self.assertEqual(data, {
                    'results': [{'id': str(o.pk), 'text': o.name}],
                    'pagination': {'more': False},
                })

    def test_to_field_resolution_with_fk_pk(self):
        """
        Tests the resolution of a foreign key field using primary key lookup in an autocomplete view.
        
        This function creates a `Parent` instance and a `PKChild` instance associated with it. It then makes a GET request to an autocomplete view with specific query parameters to search for the child's name. The function asserts that the response status code is 200 and that the returned data contains the correct child's primary key and name.
        
        Important Functions:
        - `Parent.objects.create()
        """

        p = Parent.objects.create(name="Bertie")
        c = PKChild.objects.create(parent=p, name="Anna")
        opts = {
            'app_label': Toy._meta.app_label,
            'model_name': Toy._meta.model_name,
            'field_name': 'child',
        }
        request = self.factory.get(self.url, {'term': 'anna', **opts})
        request.user = self.superuser
        response = AutocompleteJsonView.as_view(**self.as_view_args)(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, {
            'results': [{'id': str(c.pk), 'text': c.name}],
            'pagination': {'more': False},
        })

    def test_field_does_not_exist(self):
        """
        Tests if a field that does not exist is queried in an autocomplete view.
        
        This function sends a GET request to the specified URL with a term and a non-existent field name. It then checks if a `PermissionDenied` exception is raised when attempting to access the `AutocompleteJsonView`.
        
        :param self: The current instance of the test class.
        :type self: unittest.TestCase
        :param self.factory: A factory object for creating HTTP request instances.
        :type self.factory
        """

        request = self.factory.get(self.url, {'term': 'is', **self.opts, 'field_name': 'does_not_exist'})
        request.user = self.superuser
        with self.assertRaises(PermissionDenied):
            AutocompleteJsonView.as_view(**self.as_view_args)(request)

    def test_field_no_related_field(self):
        """
        Tests the behavior of the `AutocompleteJsonView` when no related field is specified in the request.
        
        Summary:
        - Input: GET request with term='is', field_name='answer'
        - User: Superuser with permission to access the view
        - Raises: PermissionDenied if no related field is provided
        
        Args:
        - request (HttpRequest): The HTTP GET request containing the search term and field name
        
        Returns:
        - None: Raises PermissionDenied exception if no
        """

        request = self.factory.get(self.url, {'term': 'is', **self.opts, 'field_name': 'answer'})
        request.user = self.superuser
        with self.assertRaises(PermissionDenied):
            AutocompleteJsonView.as_view(**self.as_view_args)(request)

    def test_field_does_not_allowed(self):
        """
        Tests if the field 'related_questions' does not allow the specified operation.
        
        This function sends a GET request to the autocomplete view with the 'related_questions' field and checks if a PermissionDenied exception is raised.
        
        Args:
        self: The current instance of the test class.
        
        Raises:
        PermissionDenied: If the field 'related_questions' allows the specified operation.
        
        Important Functions:
        - `self.factory.get`: Creates a mock HTTP GET request.
        - `AutocompleteJson
        """

        request = self.factory.get(self.url, {'term': 'is', **self.opts, 'field_name': 'related_questions'})
        request.user = self.superuser
        with self.assertRaises(PermissionDenied):
            AutocompleteJsonView.as_view(**self.as_view_args)(request)

    def test_limit_choices_to(self):
        """
        Tests the `limit_choices_to` functionality for a specific field in the `Question` model.
        
        This function creates two instances of the `Question` model with different questions. It then makes an HTTP GET request to the `AutocompleteJsonView` view with a search term 'is' and the `question_with_to_field` field. The request is made by a superuser. The function asserts that the response status code is 200 (OK) and that the returned JSON contains the
        """

        # Answer.question_with_to_field defines limit_choices_to to "those not
        # starting with 'not'".
        q = Question.objects.create(question='Is this a question?')
        Question.objects.create(question='Not a question.')
        request = self.factory.get(self.url, {'term': 'is', **self.opts, 'field_name': 'question_with_to_field'})
        request.user = self.superuser
        response = AutocompleteJsonView.as_view(**self.as_view_args)(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, {
            'results': [{'id': str(q.uuid), 'text': q.question}],
            'pagination': {'more': False},
        })

    def test_must_be_logged_in(self):
        """
        Tests if the user must be logged in to access the specified URL.
        
        Summary:
        - Uses `self.client.get` to send a GET request to the specified URL with query parameters.
        - Checks if the response status code is 200 (indicating successful login).
        - Logs out the user using `self.client.logout()`.
        - Sends another GET request to the same URL with the same query parameters after logging out.
        - Verifies that the response status code is
        """

        response = self.client.get(self.url, {'term': '', **self.opts})
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        response = self.client.get(self.url, {'term': '', **self.opts})
        self.assertEqual(response.status_code, 302)

    def test_has_view_or_change_permission_required(self):
        """
        Users require the change permission for the related model to the
        autocomplete view for it.
        """
        request = self.factory.get(self.url, {'term': 'is', **self.opts})
        request.user = self.user
        with self.assertRaises(PermissionDenied):
            AutocompleteJsonView.as_view(**self.as_view_args)(request)
        for permission in ('view', 'change'):
            with self.subTest(permission=permission):
                self.user.user_permissions.clear()
                p = Permission.objects.get(
                    content_type=ContentType.objects.get_for_model(Question),
                    codename='%s_question' % permission,
                )
                self.user.user_permissions.add(p)
                request.user = User.objects.get(pk=self.user.pk)
                response = AutocompleteJsonView.as_view(**self.as_view_args)(request)
                self.assertEqual(response.status_code, 200)

    def test_search_use_distinct(self):
        """
        Searching across model relations use QuerySet.distinct() to avoid
        duplicates.
        """
        q1 = Question.objects.create(question='question 1')
        q2 = Question.objects.create(question='question 2')
        q2.related_questions.add(q1)
        q3 = Question.objects.create(question='question 3')
        q3.related_questions.add(q1)
        request = self.factory.get(self.url, {'term': 'question', **self.opts})
        request.user = self.superuser

        class DistinctQuestionAdmin(QuestionAdmin):
            search_fields = ['related_questions__question', 'question']

        with model_admin(Question, DistinctQuestionAdmin):
            response = AutocompleteJsonView.as_view(**self.as_view_args)(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data['results']), 3)

    def test_missing_search_fields(self):
        """
        Tests that an admin class with an empty search_fields list raises a Http404 error when attempting to access the autocomplete_view.
        
        This function checks if the `EmptySearchAdmin` class, which has an empty `search_fields` attribute, will raise a `Http404` error when trying to access the `autocomplete_view`. The test is performed by creating an instance of `EmptySearchAdmin` for the `Question` model and making a GET request to the `autocomplete_view` with
        """

        class EmptySearchAdmin(QuestionAdmin):
            search_fields = []

        with model_admin(Question, EmptySearchAdmin):
            msg = 'EmptySearchAdmin must have search_fields for the autocomplete_view.'
            with self.assertRaisesMessage(Http404, msg):
                site.autocomplete_view(self.factory.get(self.url, {'term': '', **self.opts}))

    def test_get_paginator(self):
        """Search results are paginated."""
        class PKOrderingQuestionAdmin(QuestionAdmin):
            ordering = ['pk']

        Question.objects.bulk_create(Question(question=str(i)) for i in range(PAGINATOR_SIZE + 10))
        # The first page of results.
        request = self.factory.get(self.url, {'term': '', **self.opts})
        request.user = self.superuser
        with model_admin(Question, PKOrderingQuestionAdmin):
            response = AutocompleteJsonView.as_view(**self.as_view_args)(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, {
            'results': [{'id': str(q.pk), 'text': q.question} for q in Question.objects.all()[:PAGINATOR_SIZE]],
            'pagination': {'more': True},
        })
        # The second page of results.
        request = self.factory.get(self.url, {'term': '', 'page': '2', **self.opts})
        request.user = self.superuser
        with model_admin(Question, PKOrderingQuestionAdmin):
            response = AutocompleteJsonView.as_view(**self.as_view_args)(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, {
            'results': [{'id': str(q.pk), 'text': q.question} for q in Question.objects.all()[PAGINATOR_SIZE:]],
            'pagination': {'more': False},
        })


@override_settings(ROOT_URLCONF='admin_views.urls')
class SeleniumTests(AdminSeleniumTestCase):
    available_apps = ['admin_views'] + AdminSeleniumTestCase.available_apps

    def setUp(self):
        """
        Sets up test environment by creating a superuser and logging them into the admin interface.
        
        This method creates a superuser with the specified username, password, and email. It then logs the user into the admin interface using the provided credentials and login URL.
        
        :param self: The current instance of the class.
        :type self: object
        :return: None
        :rtype: None
        
        Important Functions:
        - `User.objects.create_superuser`: Creates a superuser with the
        """

        self.superuser = User.objects.create_superuser(
            username='super', password='secret', email='super@example.com',
        )
        self.admin_login(username='super', password='secret', login_url=reverse('autocomplete_admin:index'))

    @contextmanager
    def select2_ajax_wait(self, timeout=10):
        """
        Wait for the loading element of a Select2 dropdown to disappear.
        
        This function waits until the loading element, identified by the CSS selector 'li.select2-results__option.loading-results', disappears from the page. It uses an explicit wait with the `staleness_of` condition to check if the element is no longer present. The function temporarily disables implicit waits using the `disable_implicit_wait` context manager to ensure that the wait is not affected by any existing implicit wait settings.
        
        Args:
        """

        from selenium.common.exceptions import NoSuchElementException
        from selenium.webdriver.support import expected_conditions as ec
        yield
        with self.disable_implicit_wait():
            try:
                loading_element = self.selenium.find_element_by_css_selector(
                    'li.select2-results__option.loading-results'
                )
            except NoSuchElementException:
                pass
            else:
                self.wait_until(ec.staleness_of(loading_element), timeout=timeout)

    def test_select(self):
        """
        Tests the behavior of the Select2 widget in an admin form.
        
        This function tests the following functionalities:
        - Opening and closing the autocomplete dropdown.
        - Displaying and searching through paginated results.
        - Limiting search results using a search field.
        - Selecting an option from the dropdown.
        
        Important functions used:
        - `find_element_by_css_selector`: Locates elements based on CSS selectors.
        - `click`: Triggers a click event on an element.
        -
        """

        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import Select
        self.selenium.get(self.live_server_url + reverse('autocomplete_admin:admin_views_answer_add'))
        elem = self.selenium.find_element_by_css_selector('.select2-selection')
        elem.click()  # Open the autocomplete dropdown.
        results = self.selenium.find_element_by_css_selector('.select2-results')
        self.assertTrue(results.is_displayed())
        option = self.selenium.find_element_by_css_selector('.select2-results__option')
        self.assertEqual(option.text, 'No results found')
        elem.click()  # Close the autocomplete dropdown.
        q1 = Question.objects.create(question='Who am I?')
        Question.objects.bulk_create(Question(question=str(i)) for i in range(PAGINATOR_SIZE + 10))
        elem.click()  # Reopen the dropdown now that some objects exist.
        result_container = self.selenium.find_element_by_css_selector('.select2-results')
        self.assertTrue(result_container.is_displayed())
        results = result_container.find_elements_by_css_selector('.select2-results__option')
        # PAGINATOR_SIZE results and "Loading more results".
        self.assertEqual(len(results), PAGINATOR_SIZE + 1)
        search = self.selenium.find_element_by_css_selector('.select2-search__field')
        # Load next page of results by scrolling to the bottom of the list.
        with self.select2_ajax_wait():
            for _ in range(len(results)):
                search.send_keys(Keys.ARROW_DOWN)
        results = result_container.find_elements_by_css_selector('.select2-results__option')
        # All objects are now loaded.
        self.assertEqual(len(results), PAGINATOR_SIZE + 11)
        # Limit the results with the search field.
        with self.select2_ajax_wait():
            search.send_keys('Who')
            # Ajax request is delayed.
            self.assertTrue(result_container.is_displayed())
            results = result_container.find_elements_by_css_selector('.select2-results__option')
            self.assertEqual(len(results), PAGINATOR_SIZE + 12)
        self.assertTrue(result_container.is_displayed())
        results = result_container.find_elements_by_css_selector('.select2-results__option')
        self.assertEqual(len(results), 1)
        # Select the result.
        search.send_keys(Keys.RETURN)
        select = Select(self.selenium.find_element_by_id('id_question'))
        self.assertEqual(select.first_selected_option.get_attribute('value'), str(q1.pk))

    def test_select_multiple(self):
        """
        Tests the functionality of selecting multiple options in an autocomplete dropdown using Selenium.
        
        This test ensures that the autocomplete dropdown opens and displays results correctly, handles pagination,
        and allows for multiple selections. It uses the `Select` class from Selenium to manage the selection process.
        
        :param self: The current instance of the test case.
        """

        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import Select
        self.selenium.get(self.live_server_url + reverse('autocomplete_admin:admin_views_question_add'))
        elem = self.selenium.find_element_by_css_selector('.select2-selection')
        elem.click()  # Open the autocomplete dropdown.
        results = self.selenium.find_element_by_css_selector('.select2-results')
        self.assertTrue(results.is_displayed())
        option = self.selenium.find_element_by_css_selector('.select2-results__option')
        self.assertEqual(option.text, 'No results found')
        elem.click()  # Close the autocomplete dropdown.
        Question.objects.create(question='Who am I?')
        Question.objects.bulk_create(Question(question=str(i)) for i in range(PAGINATOR_SIZE + 10))
        elem.click()  # Reopen the dropdown now that some objects exist.
        result_container = self.selenium.find_element_by_css_selector('.select2-results')
        self.assertTrue(result_container.is_displayed())
        results = result_container.find_elements_by_css_selector('.select2-results__option')
        self.assertEqual(len(results), PAGINATOR_SIZE + 1)
        search = self.selenium.find_element_by_css_selector('.select2-search__field')
        # Load next page of results by scrolling to the bottom of the list.
        with self.select2_ajax_wait():
            for _ in range(len(results)):
                search.send_keys(Keys.ARROW_DOWN)
        results = result_container.find_elements_by_css_selector('.select2-results__option')
        self.assertEqual(len(results), 31)
        # Limit the results with the search field.
        with self.select2_ajax_wait():
            search.send_keys('Who')
            # Ajax request is delayed.
            self.assertTrue(result_container.is_displayed())
            results = result_container.find_elements_by_css_selector('.select2-results__option')
            self.assertEqual(len(results), 32)
        self.assertTrue(result_container.is_displayed())
        results = result_container.find_elements_by_css_selector('.select2-results__option')
        self.assertEqual(len(results), 1)
        # Select the result.
        search.send_keys(Keys.RETURN)
        # Reopen the dropdown and add the first result to the selection.
        elem.click()
        search.send_keys(Keys.ARROW_DOWN)
        search.send_keys(Keys.RETURN)
        select = Select(self.selenium.find_element_by_id('id_related_questions'))
        self.assertEqual(len(select.all_selected_options), 2)

    def test_inline_add_another_widgets(self):
        """
        Tests the inline add another widgets functionality for an autocomplete field.
        
        This function checks if the autocomplete dropdown is properly displayed and
        shows 'No results found' message for new rows added via the "Add another"
        button. It involves interacting with elements like `.dynamic-authorship_set`,
        `.select2-selection`, and `.select2-results` to verify the behavior of the
        autocomplete feature.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `
        """

        def assertNoResults(row):
            """
            Asserts that no search results are found for a given row.
            
            Args:
            row (WebElement): The row element on the page containing the select2 input.
            
            This function opens the autocomplete dropdown by clicking on the select2 input element, then checks if the results container is displayed. If results are displayed, it further checks if the first option text matches 'No results found'.
            """

            elem = row.find_element_by_css_selector('.select2-selection')
            elem.click()  # Open the autocomplete dropdown.
            results = self.selenium.find_element_by_css_selector('.select2-results')
            self.assertTrue(results.is_displayed())
            option = self.selenium.find_element_by_css_selector('.select2-results__option')
            self.assertEqual(option.text, 'No results found')

        # Autocomplete works in rows present when the page loads.
        self.selenium.get(self.live_server_url + reverse('autocomplete_admin:admin_views_book_add'))
        rows = self.selenium.find_elements_by_css_selector('.dynamic-authorship_set')
        self.assertEqual(len(rows), 3)
        assertNoResults(rows[0])
        # Autocomplete works in rows added using the "Add another" button.
        self.selenium.find_element_by_link_text('Add another Authorship').click()
        rows = self.selenium.find_elements_by_css_selector('.dynamic-authorship_set')
        self.assertEqual(len(rows), 4)
        assertNoResults(rows[-1])
