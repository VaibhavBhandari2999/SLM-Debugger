import datetime

from django import forms
from django.core.validators import ValidationError
from django.forms.models import ModelChoiceIterator
from django.forms.widgets import CheckboxSelectMultiple
from django.template import Context, Template
from django.test import TestCase

from .models import Article, Author, Book, Category, Writer


class ModelChoiceFieldTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Sets up test data for category objects. Creates three Category instances with predefined names, slugs, and URLs. The created categories are stored in class attributes (cls.c1, cls.c2, cls.c3) for use in tests.
        
        Args:
        cls: The test case class instance.
        
        Returns:
        None
        
        Important Functions:
        - `Category.objects.create`: Used to create new category instances.
        
        Class Attributes:
        - `cls.c1`: First category instance.
        """

        cls.c1 = Category.objects.create(name='Entertainment', slug='entertainment', url='entertainment')
        cls.c2 = Category.objects.create(name='A test', slug='test', url='test')
        cls.c3 = Category.objects.create(name='Third', slug='third-test', url='third')

    def test_basics(self):
        """
        Tests basic functionality of ModelChoiceField.
        
        - Verifies the choices are correctly populated from the queryset.
        - Ensures invalid inputs raise ValidationError.
        - Confirms valid IDs return corresponding model instances.
        - Demonstrates dynamic validation by adding and deleting categories.
        """

        f = forms.ModelChoiceField(Category.objects.all())
        self.assertEqual(list(f.choices), [
            ('', '---------'),
            (self.c1.pk, 'Entertainment'),
            (self.c2.pk, 'A test'),
            (self.c3.pk, 'Third'),
        ])
        with self.assertRaises(ValidationError):
            f.clean('')
        with self.assertRaises(ValidationError):
            f.clean(None)
        with self.assertRaises(ValidationError):
            f.clean(0)

        # Invalid types that require TypeError to be caught.
        with self.assertRaises(ValidationError):
            f.clean([['fail']])
        with self.assertRaises(ValidationError):
            f.clean([{'foo': 'bar'}])

        self.assertEqual(f.clean(self.c2.id).name, 'A test')
        self.assertEqual(f.clean(self.c3.id).name, 'Third')

        # Add a Category object *after* the ModelChoiceField has already been
        # instantiated. This proves clean() checks the database during clean()
        # rather than caching it at  instantiation time.
        c4 = Category.objects.create(name='Fourth', url='4th')
        self.assertEqual(f.clean(c4.id).name, 'Fourth')

        # Delete a Category object *after* the ModelChoiceField has already been
        # instantiated. This proves clean() checks the database during clean()
        # rather than caching it at instantiation time.
        Category.objects.get(url='4th').delete()
        msg = "['Select a valid choice. That choice is not one of the available choices.']"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean(c4.id)

    def test_clean_model_instance(self):
        """
        Tests the cleaning functionality of a ModelChoiceField. The function creates an instance of ModelChoiceField with all Category objects and checks if it correctly cleans a valid Category instance. It also tests that an instance of an incorrect model (Book) raises a ValidationError with a specific message.
        """

        f = forms.ModelChoiceField(Category.objects.all())
        self.assertEqual(f.clean(self.c1), self.c1)
        # An instance of incorrect model.
        msg = "['Select a valid choice. That choice is not one of the available choices.']"
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean(Book.objects.create())

    def test_clean_to_field_name(self):
        """
        Tests the `clean` method of a ModelChoiceField with `to_field_name` set to 'slug'.
        
        Args:
        self: The instance of the test case.
        
        Inputs:
        - `f`: A ModelChoiceField instance configured to use Category model and filter by all categories, with `to_field_name` set to 'slug'.
        - `self.c1.slug`: A slug value representing a category instance.
        - `self.c1`: A category instance.
        
        Outputs:
        """

        f = forms.ModelChoiceField(Category.objects.all(), to_field_name='slug')
        self.assertEqual(f.clean(self.c1.slug), self.c1)
        self.assertEqual(f.clean(self.c1), self.c1)

    def test_choices(self):
        """
        Tests various functionalities of ModelChoiceField.
        
        This function tests the following aspects of ModelChoiceField:
        - Cleaning empty and valid choices
        - Checking the length of choices
        - Changing the queryset after field creation
        - Iterating over choices multiple times
        - Customizing choice labels using label_from_instance
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - clean: Validates and cleans input values.
        - len: Checks the number of choices
        """

        f = forms.ModelChoiceField(Category.objects.filter(pk=self.c1.id), required=False)
        self.assertIsNone(f.clean(''))
        self.assertEqual(f.clean(str(self.c1.id)).name, 'Entertainment')
        with self.assertRaises(ValidationError):
            f.clean('100')

        # len() can be called on choices.
        self.assertEqual(len(f.choices), 2)

        # queryset can be changed after the field is created.
        f.queryset = Category.objects.exclude(name='Third')
        self.assertEqual(list(f.choices), [
            ('', '---------'),
            (self.c1.pk, 'Entertainment'),
            (self.c2.pk, 'A test'),
        ])
        self.assertEqual(f.clean(self.c2.id).name, 'A test')
        with self.assertRaises(ValidationError):
            f.clean(self.c3.id)

        # Choices can be iterated repeatedly.
        gen_one = list(f.choices)
        gen_two = f.choices
        self.assertEqual(gen_one[2], (self.c2.pk, 'A test'))
        self.assertEqual(list(gen_two), [
            ('', '---------'),
            (self.c1.pk, 'Entertainment'),
            (self.c2.pk, 'A test'),
        ])

        # Overriding label_from_instance() to print custom labels.
        f.queryset = Category.objects.all()
        f.label_from_instance = lambda obj: 'category ' + str(obj)
        self.assertEqual(list(f.choices), [
            ('', '---------'),
            (self.c1.pk, 'category Entertainment'),
            (self.c2.pk, 'category A test'),
            (self.c3.pk, 'category Third'),
        ])

    def test_choices_freshness(self):
        """
        Tests the freshness of choices in a ModelChoiceField.
        
        This function creates a `ModelChoiceField` with all categories from the database,
        checks its initial choice count and content, then adds a new category and verifies
        that the field's choices are updated accordingly.
        
        - `forms.ModelChoiceField`: The form field being tested.
        - `Category.objects.all()`: The queryset of all categories.
        - `self.assertEqual`: Asserts the equality of expected and actual values.
        """

        f = forms.ModelChoiceField(Category.objects.all())
        self.assertEqual(len(f.choices), 4)
        self.assertEqual(list(f.choices), [
            ('', '---------'),
            (self.c1.pk, 'Entertainment'),
            (self.c2.pk, 'A test'),
            (self.c3.pk, 'Third'),
        ])
        c4 = Category.objects.create(name='Fourth', slug='4th', url='4th')
        self.assertEqual(len(f.choices), 5)
        self.assertEqual(list(f.choices), [
            ('', '---------'),
            (self.c1.pk, 'Entertainment'),
            (self.c2.pk, 'A test'),
            (self.c3.pk, 'Third'),
            (c4.pk, 'Fourth'),
        ])

    def test_choices_bool(self):
        """
        Tests the boolean value of a ModelChoiceField's choices.
        
        This function checks whether the boolean value of the choices attribute
        of a ModelChoiceField instance is affected by the presence or absence
        of categories in the database. It creates an instance of
        ModelChoiceField with all categories, then verifies that its choices
        are truthy. After deleting all categories from the database, it
        confirms that the choices are falsy.
        
        Args:
        None
        
        Returns:
        """

        f = forms.ModelChoiceField(Category.objects.all(), empty_label=None)
        self.assertIs(bool(f.choices), True)
        Category.objects.all().delete()
        self.assertIs(bool(f.choices), False)

    def test_choices_bool_empty_label(self):
        """
        Tests the behavior of a ModelChoiceField with an empty label when all categories are deleted.
        
        Args:
        None
        
        Returns:
        None
        
        Summary:
        This function creates a ModelChoiceField instance with `Category` objects and an empty label. It then deletes all `Category` objects and checks if the choices attribute of the field is still truthy, indicating that the field still contains some choices despite the deletion.
        
        Functions Used:
        - forms.ModelChoiceField
        - Category
        """

        f = forms.ModelChoiceField(Category.objects.all(), empty_label='--------')
        Category.objects.all().delete()
        self.assertIs(bool(f.choices), True)

    def test_deepcopies_widget(self):
        """
        Tests deep copies of a form's fields and their associated widgets.
        
        This function creates an instance of `ModelChoiceForm`, extracts the `category` field, and verifies that the field and its widget maintain distinct references. It ensures that changes to the widget's choices do not affect other forms by checking that the `field1` and `ModelChoiceForm.base_fields['category']` are not the same object.
        """

        class ModelChoiceForm(forms.Form):
            category = forms.ModelChoiceField(Category.objects.all())

        form1 = ModelChoiceForm()
        field1 = form1.fields['category']
        # To allow the widget to change the queryset of field1.widget.choices
        # without affecting other forms, the following must hold (#11183):
        self.assertIsNot(field1, ModelChoiceForm.base_fields['category'])
        self.assertIs(field1.widget.choices.field, field1)

    def test_result_cache_not_shared(self):
        """
        Tests that the queryset cache for a ModelChoiceField is not shared between instances.
        
        This function creates two instances of `ModelChoiceForm` and checks that the queryset cache
        for the 'category' field is not shared between them. The important functions used are
        `assertCountEqual` and `ModelChoiceField`.
        """

        class ModelChoiceForm(forms.Form):
            category = forms.ModelChoiceField(Category.objects.all())

        form1 = ModelChoiceForm()
        self.assertCountEqual(form1.fields['category'].queryset, [self.c1, self.c2, self.c3])
        form2 = ModelChoiceForm()
        self.assertIsNone(form2.fields['category'].queryset._result_cache)

    def test_queryset_none(self):
        """
        Tests that the queryset for a ModelChoiceField is correctly set after form initialization.
        
        This function creates an instance of `ModelChoiceForm` with a `ModelChoiceField` whose initial queryset is set to `None`. During form initialization, the queryset is dynamically updated to filter categories by slug containing 'test'. The function asserts that the final queryset contains only the expected categories (`self.c2` and `self.c3`).
        
        :param self: The current test case instance.
        :type
        """

        class ModelChoiceForm(forms.Form):
            category = forms.ModelChoiceField(queryset=None)

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.fields['category'].queryset = Category.objects.filter(slug__contains='test')

        form = ModelChoiceForm()
        self.assertCountEqual(form.fields['category'].queryset, [self.c2, self.c3])

    def test_no_extra_query_when_accessing_attrs(self):
        """
        ModelChoiceField with RadioSelect widget doesn't produce unnecessary
        db queries when accessing its BoundField's attrs.
        """
        class ModelChoiceForm(forms.Form):
            category = forms.ModelChoiceField(Category.objects.all(), widget=forms.RadioSelect)

        form = ModelChoiceForm()
        field = form['category']  # BoundField
        template = Template('{{ field.name }}{{ field }}{{ field.help_text }}')
        with self.assertNumQueries(1):
            template.render(Context({'field': field}))

    def test_disabled_modelchoicefield(self):
        """
        Tests the behavior of a disabled ModelChoiceField in a form.
        
        This function creates a form with a disabled ModelChoiceField for the 'author' field,
        and checks if the form validation fails when an invalid choice is submitted. The form
        is instantiated with an existing Book instance, and the errors for the 'author' field
        are expected to indicate that a valid choice was not selected.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        """

        class ModelChoiceForm(forms.ModelForm):
            author = forms.ModelChoiceField(Author.objects.all(), disabled=True)

            class Meta:
                model = Book
                fields = ['author']

        book = Book.objects.create(author=Writer.objects.create(name='Test writer'))
        form = ModelChoiceForm({}, instance=book)
        self.assertEqual(
            form.errors['author'],
            ['Select a valid choice. That choice is not one of the available choices.']
        )

    def test_disabled_modelchoicefield_has_changed(self):
        field = forms.ModelChoiceField(Author.objects.all(), disabled=True)
        self.assertIs(field.has_changed('x', 'y'), False)

    def test_disabled_modelchoicefield_initial_model_instance(self):
        """
        Tests the validation of a disabled ModelChoiceField with an initial model instance.
        
        This function creates a form with a disabled ModelChoiceField that is initialized with a specific model instance (self.c1). It then validates the form with data containing the primary key of the initial model instance and checks if the form is valid.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - ModelChoiceForm: A form with a disabled ModelChoiceField.
        - is_valid():
        """

        class ModelChoiceForm(forms.Form):
            categories = forms.ModelChoiceField(
                Category.objects.all(),
                disabled=True,
                initial=self.c1,
            )

        self.assertTrue(ModelChoiceForm(data={'categories': self.c1.pk}).is_valid())

    def test_disabled_multiplemodelchoicefield(self):
        """
        Tests the behavior of a disabled ModelMultipleChoiceField in a form.
        
        This function verifies that when a ModelMultipleChoiceField is disabled,
        its value is taken from the form's instance rather than the submitted data.
        It creates an ArticleForm with a disabled 'categories' field and checks
        that the cleaned data reflects the instance's categories instead of the
        provided data.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - ModelMultipleChoiceField
        """

        class ArticleForm(forms.ModelForm):
            categories = forms.ModelMultipleChoiceField(Category.objects.all(), required=False)

            class Meta:
                model = Article
                fields = ['categories']

        category1 = Category.objects.create(name='cat1')
        category2 = Category.objects.create(name='cat2')
        article = Article.objects.create(
            pub_date=datetime.date(1988, 1, 4),
            writer=Writer.objects.create(name='Test writer'),
        )
        article.categories.set([category1.pk])

        form = ArticleForm(data={'categories': [category2.pk]}, instance=article)
        self.assertEqual(form.errors, {})
        self.assertEqual([x.pk for x in form.cleaned_data['categories']], [category2.pk])
        # Disabled fields use the value from `instance` rather than `data`.
        form = ArticleForm(data={'categories': [category2.pk]}, instance=article)
        form.fields['categories'].disabled = True
        self.assertEqual(form.errors, {})
        self.assertEqual([x.pk for x in form.cleaned_data['categories']], [category1.pk])

    def test_disabled_modelmultiplechoicefield_has_changed(self):
        field = forms.ModelMultipleChoiceField(Author.objects.all(), disabled=True)
        self.assertIs(field.has_changed('x', 'y'), False)

    def test_overridable_choice_iterator(self):
        """
        Iterator defaults to ModelChoiceIterator and can be overridden with
        the iterator attribute on a ModelChoiceField subclass.
        """
        field = forms.ModelChoiceField(Category.objects.all())
        self.assertIsInstance(field.choices, ModelChoiceIterator)

        class CustomModelChoiceIterator(ModelChoiceIterator):
            pass

        class CustomModelChoiceField(forms.ModelChoiceField):
            iterator = CustomModelChoiceIterator

        field = CustomModelChoiceField(Category.objects.all())
        self.assertIsInstance(field.choices, CustomModelChoiceIterator)

    def test_choice_iterator_passes_model_to_widget(self):
        """
        Tests that the `CustomCheckboxSelectMultiple` widget correctly passes the model instance to the `create_option` method during rendering.
        
        This function creates a custom checkbox select multiple widget that modifies the HTML attributes of each option based on the model instance being rendered. It then tests this widget by asserting the rendered HTML matches the expected output.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `CustomCheckboxSelectMultiple`: A custom widget that extends `CheckboxSelectMultiple`.
        """

        class CustomCheckboxSelectMultiple(CheckboxSelectMultiple):
            def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
                """
                Create an option element for a select widget.
                
                This method is overridden to modify the generated HTML by adding a `data-slug` attribute to the option element. The `data-slug` attribute is set based on the instance of the object associated with the option's value.
                
                Args:
                name (str): The name of the option.
                value (object): The value of the option, typically an instance of a model.
                label (str): The text label for the option.
                """

                option = super().create_option(name, value, label, selected, index, subindex, attrs)
                # Modify the HTML based on the object being rendered.
                c = value.instance
                option['attrs']['data-slug'] = c.slug
                return option

        class CustomModelMultipleChoiceField(forms.ModelMultipleChoiceField):
            widget = CustomCheckboxSelectMultiple

        field = CustomModelMultipleChoiceField(Category.objects.all())
        self.assertHTMLEqual(
            field.widget.render('name', []), (
                '<ul>'
                '<li><label><input type="checkbox" name="name" value="%d" '
                'data-slug="entertainment">Entertainment</label></li>'
                '<li><label><input type="checkbox" name="name" value="%d" '
                'data-slug="test">A test</label></li>'
                '<li><label><input type="checkbox" name="name" value="%d" '
                'data-slug="third-test">Third</label></li>'
                '</ul>'
            ) % (self.c1.pk, self.c2.pk, self.c3.pk),
        )

    def test_custom_choice_iterator_passes_model_to_widget(self):
        """
        Tests the `CustomModelMultipleChoiceField` widget rendering with a custom choice iterator.
        
        This function verifies that the `CustomModelMultipleChoiceField` widget correctly renders options using a custom choice iterator and a modified checkbox select multiple widget. The custom choice iterator returns a `CustomModelChoiceValue` object, and the widget adds additional attributes to the rendered checkboxes based on the model instance.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `CustomModelChoiceValue
        """

        class CustomModelChoiceValue:
            def __init__(self, value, obj):
                self.value = value
                self.obj = obj

            def __str__(self):
                return str(self.value)

        class CustomModelChoiceIterator(ModelChoiceIterator):
            def choice(self, obj):
                value, label = super().choice(obj)
                return CustomModelChoiceValue(value, obj), label

        class CustomCheckboxSelectMultiple(CheckboxSelectMultiple):
            def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
                option = super().create_option(name, value, label, selected, index, subindex, attrs)
                # Modify the HTML based on the object being rendered.
                c = value.obj
                option['attrs']['data-slug'] = c.slug
                return option

        class CustomModelMultipleChoiceField(forms.ModelMultipleChoiceField):
            iterator = CustomModelChoiceIterator
            widget = CustomCheckboxSelectMultiple

        field = CustomModelMultipleChoiceField(Category.objects.all())
        self.assertHTMLEqual(
            field.widget.render('name', []),
            '''<ul>
<li><label><input type="checkbox" name="name" value="%d" data-slug="entertainment">Entertainment</label></li>
<li><label><input type="checkbox" name="name" value="%d" data-slug="test">A test</label></li>
<li><label><input type="checkbox" name="name" value="%d" data-slug="third-test">Third</label></li>
</ul>''' % (self.c1.pk, self.c2.pk, self.c3.pk),
        )

    def test_choices_not_fetched_when_not_rendering(self):
        """
        Tests that choices are not fetched from the database when the field is not being rendered.
        
        This function asserts that only one query is executed, indicating that the choices are not fetched from the database. It creates an instance of `ModelChoiceField` with pre-fetched categories ordered by name and then cleans the primary key of category 'c1' to ensure it returns the correct name ('Entertainment').
        """

        with self.assertNumQueries(1):
            field = forms.ModelChoiceField(Category.objects.order_by('-name'))
            self.assertEqual('Entertainment', field.clean(self.c1.pk).name)

    def test_queryset_manager(self):
        """
        Tests the queryset manager of a ModelChoiceField form.
        
        This function creates an instance of ModelChoiceField with a queryset of Category objects. It then checks that the length of the choices list is 4 and verifies that the choices match the expected values, including the default empty label and the primary keys and names of the categories.
        """

        f = forms.ModelChoiceField(Category.objects)
        self.assertEqual(len(f.choices), 4)
        self.assertEqual(list(f.choices), [
            ('', '---------'),
            (self.c1.pk, 'Entertainment'),
            (self.c2.pk, 'A test'),
            (self.c3.pk, 'Third'),
        ])

    def test_num_queries(self):
        """
        Widgets that render multiple subwidgets shouldn't make more than one
        database query.
        """
        categories = Category.objects.all()

        class CategoriesForm(forms.Form):
            radio = forms.ModelChoiceField(queryset=categories, widget=forms.RadioSelect)
            checkbox = forms.ModelMultipleChoiceField(queryset=categories, widget=forms.CheckboxSelectMultiple)

        template = Template(
            '{% for widget in form.checkbox %}{{ widget }}{% endfor %}'
            '{% for widget in form.radio %}{{ widget }}{% endfor %}'
        )
        with self.assertNumQueries(2):
            template.render(Context({'form': CategoriesForm()}))
