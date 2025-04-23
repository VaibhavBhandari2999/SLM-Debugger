import datetime

from django.contrib.admin import ModelAdmin
from django.contrib.admin.templatetags.admin_list import date_hierarchy
from django.contrib.admin.templatetags.admin_modify import submit_row
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from .admin import ArticleAdmin, site
from .models import Article, Question
from .tests import AdminViewBasicTestCase


class AdminTemplateTagsTest(AdminViewBasicTestCase):
    request_factory = RequestFactory()

    def test_submit_row(self):
        """
        submit_row template tag should pass whole context.
        """
        request = self.request_factory.get(
            reverse("admin:auth_user_change", args=[self.superuser.pk])
        )
        request.user = self.superuser
        admin = UserAdmin(User, site)
        extra_context = {"extra": True}
        response = admin.change_view(
            request, str(self.superuser.pk), extra_context=extra_context
        )
        template_context = submit_row(response.context_data)
        self.assertIs(template_context["extra"], True)
        self.assertIs(template_context["show_save"], True)

    def test_override_show_save_and_add_another(self):
        """
        Tests the behavior of the 'change_view' method in the UserAdmin class for displaying the 'show_save_and_add_another' flag.
        
        This function verifies that the 'show_save_and_add_another' flag is correctly overridden based on the provided extra context. It checks two scenarios:
        1. The default behavior when no extra context is provided.
        2. The behavior when the 'show_save_and_add_another' flag is explicitly set to False in the extra context.
        
        Parameters:
        - request (Request
        """

        request = self.request_factory.get(
            reverse("admin:auth_user_change", args=[self.superuser.pk]),
        )
        request.user = self.superuser
        admin = UserAdmin(User, site)
        for extra_context, expected_flag in (
            ({}, True),  # Default.
            ({"show_save_and_add_another": False}, False),
        ):
            with self.subTest(show_save_and_add_another=expected_flag):
                response = admin.change_view(
                    request,
                    str(self.superuser.pk),
                    extra_context=extra_context,
                )
                template_context = submit_row(response.context_data)
                self.assertIs(
                    template_context["show_save_and_add_another"], expected_flag
                )

    def test_override_change_form_template_tags(self):
        """
        admin_modify template tags follow the standard search pattern
        admin/app_label/model/template.html.
        """
        article = Article.objects.all()[0]
        request = self.request_factory.get(
            reverse("admin:admin_views_article_change", args=[article.pk])
        )
        request.user = self.superuser
        admin = ArticleAdmin(Article, site)
        extra_context = {"show_publish": True, "extra": True}
        response = admin.change_view(
            request, str(article.pk), extra_context=extra_context
        )
        response.render()
        self.assertIs(response.context_data["show_publish"], True)
        self.assertIs(response.context_data["extra"], True)
        self.assertContains(response, 'name="_save"')
        self.assertContains(response, 'name="_publish"')
        self.assertContains(response, "override-change_form_object_tools")
        self.assertContains(response, "override-prepopulated_fields_js")

    def test_override_change_list_template_tags(self):
        """
        admin_list template tags follow the standard search pattern
        admin/app_label/model/template.html.
        """
        request = self.request_factory.get(
            reverse("admin:admin_views_article_changelist")
        )
        request.user = self.superuser
        admin = ArticleAdmin(Article, site)
        admin.date_hierarchy = "date"
        admin.search_fields = ("title", "content")
        response = admin.changelist_view(request)
        response.render()
        self.assertContains(response, "override-actions")
        self.assertContains(response, "override-change_list_object_tools")
        self.assertContains(response, "override-change_list_results")
        self.assertContains(response, "override-date_hierarchy")
        self.assertContains(response, "override-pagination")
        self.assertContains(response, "override-search_form")


class DateHierarchyTests(TestCase):
    factory = RequestFactory()

    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser(
            username="super", password="secret", email="super@example.com"
        )

    def test_choice_links(self):
        """
        Tests the functionality of the date hierarchy in a ModelAdmin for the Question model.
        
        This function tests the generation of date hierarchy links for the Question model in a Django admin interface. It creates a set of test cases to check the correct generation of links based on the provided query parameters.
        
        Parameters:
        - None (the function uses internal test data and Django framework objects)
        
        Returns:
        - None (the function asserts the correctness of the generated links)
        
        Key Parameters:
        - modeladmin: The ModelAdmin instance for the
        """

        modeladmin = ModelAdmin(Question, site)
        modeladmin.date_hierarchy = "posted"

        posted_dates = (
            datetime.date(2017, 10, 1),
            datetime.date(2017, 10, 1),
            datetime.date(2017, 12, 15),
            datetime.date(2017, 12, 15),
            datetime.date(2017, 12, 31),
            datetime.date(2018, 2, 1),
        )
        Question.objects.bulk_create(
            Question(question="q", posted=posted) for posted in posted_dates
        )

        tests = (
            ({}, [["year=2017"], ["year=2018"]]),
            ({"year": 2016}, []),
            ({"year": 2017}, [["month=10", "year=2017"], ["month=12", "year=2017"]]),
            ({"year": 2017, "month": 9}, []),
            (
                {"year": 2017, "month": 12},
                [
                    ["day=15", "month=12", "year=2017"],
                    ["day=31", "month=12", "year=2017"],
                ],
            ),
        )
        for query, expected_choices in tests:
            with self.subTest(query=query):
                query = {"posted__%s" % q: val for q, val in query.items()}
                request = self.factory.get("/", query)
                request.user = self.superuser
                changelist = modeladmin.get_changelist_instance(request)
                spec = date_hierarchy(changelist)
                choices = [choice["link"] for choice in spec["choices"]]
                expected_choices = [
                    "&".join("posted__%s" % c for c in choice)
                    for choice in expected_choices
                ]
                expected_choices = [
                    ("?" + choice) if choice else "" for choice in expected_choices
                ]
                self.assertEqual(choices, expected_choices)

    def test_choice_links_datetime(self):
        modeladmin = ModelAdmin(Question, site)
        modeladmin.date_hierarchy = "expires"
        Question.objects.bulk_create(
            [
                Question(question="q1", expires=datetime.datetime(2017, 10, 1)),
                Question(question="q2", expires=datetime.datetime(2017, 10, 1)),
                Question(question="q3", expires=datetime.datetime(2017, 12, 15)),
                Question(question="q4", expires=datetime.datetime(2017, 12, 15)),
                Question(question="q5", expires=datetime.datetime(2017, 12, 31)),
                Question(question="q6", expires=datetime.datetime(2018, 2, 1)),
            ]
        )
        tests = [
            ({}, [["year=2017"], ["year=2018"]]),
            ({"year": 2016}, []),
            (
                {"year": 2017},
                [
                    ["month=10", "year=2017"],
                    ["month=12", "year=2017"],
                ],
            ),
            ({"year": 2017, "month": 9}, []),
            (
                {"year": 2017, "month": 12},
                [
                    ["day=15", "month=12", "year=2017"],
                    ["day=31", "month=12", "year=2017"],
                ],
            ),
        ]
        for query, expected_choices in tests:
            with self.subTest(query=query):
                query = {"expires__%s" % q: val for q, val in query.items()}
                request = self.factory.get("/", query)
                request.user = self.superuser
                changelist = modeladmin.get_changelist_instance(request)
                spec = date_hierarchy(changelist)
                choices = [choice["link"] for choice in spec["choices"]]
                expected_choices = [
                    "?" + "&".join("expires__%s" % c for c in choice)
                    for choice in expected_choices
                ]
                self.assertEqual(choices, expected_choices)
