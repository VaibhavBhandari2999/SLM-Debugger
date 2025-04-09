from django import forms
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.test import TestCase
from django.test.utils import isolate_apps

from .models import (
    Animal, ForProxyModelModel, Gecko, Mineral, ProxyRelatedModel, TaggedItem,
)


class CustomWidget(forms.TextInput):
    pass


class TaggedItemForm(forms.ModelForm):
    class Meta:
        model = TaggedItem
        fields = '__all__'
        widgets = {'tag': CustomWidget}


class GenericInlineFormsetTests(TestCase):

    def test_output(self):
        """
        <p><label for="id_generic_relations-taggeditem-content_type-object_id-0-tag">
        Tag:</label> <input id="id_generic_relations-taggeditem-content_type-object_id-0-tag" type="text"
        name="generic_relations-taggeditem-content_type-object_id-0-tag" maxlength="50"></p>
        <p><label for="id_generic_relations-taggeditem-content_type-object_id-0-DELETE">Delete:</label>
        <input type="checkbox" name="generic_relations-taggeditem-content_type-object_id-0-DELETE"
        id="id_generic_relations-taggeditem-content_type-object_id-0-DELETE">
        <input type="hidden" name="generic_relations-taggeditem-content_type-object_id-0-id"
        id="id_generic_relations-taggeditem-content_type-object_id-0-id"></p>
        """

        GenericFormSet = generic_inlineformset_factory(TaggedItem, extra=1)
        formset = GenericFormSet()
        self.assertHTMLEqual(
            ''.join(form.as_p() for form in formset.forms),
            """<p><label for="id_generic_relations-taggeditem-content_type-object_id-0-tag">
Tag:</label> <input id="id_generic_relations-taggeditem-content_type-object_id-0-tag" type="text"
name="generic_relations-taggeditem-content_type-object_id-0-tag" maxlength="50"></p>
<p><label for="id_generic_relations-taggeditem-content_type-object_id-0-DELETE">Delete:</label>
<input type="checkbox" name="generic_relations-taggeditem-content_type-object_id-0-DELETE"
id="id_generic_relations-taggeditem-content_type-object_id-0-DELETE">
<input type="hidden" name="generic_relations-taggeditem-content_type-object_id-0-id"
id="id_generic_relations-taggeditem-content_type-object_id-0-id"></p>"""
        )
        formset = GenericFormSet(instance=Animal())
        self.assertHTMLEqual(
            ''.join(form.as_p() for form in formset.forms),
            """<p><label for="id_generic_relations-taggeditem-content_type-object_id-0-tag">
Tag:</label> <input id="id_generic_relations-taggeditem-content_type-object_id-0-tag"
type="text" name="generic_relations-taggeditem-content_type-object_id-0-tag" maxlength="50"></p>
<p><label for="id_generic_relations-taggeditem-content_type-object_id-0-DELETE">Delete:</label>
<input type="checkbox" name="generic_relations-taggeditem-content_type-object_id-0-DELETE"
id="id_generic_relations-taggeditem-content_type-object_id-0-DELETE"><input type="hidden"
name="generic_relations-taggeditem-content_type-object_id-0-id"
id="id_generic_relations-taggeditem-content_type-object_id-0-id"></p>"""
        )
        platypus = Animal.objects.create(
            common_name='Platypus', latin_name='Ornithorhynchus anatinus',
        )
        platypus.tags.create(tag='shiny')
        GenericFormSet = generic_inlineformset_factory(TaggedItem, extra=1)
        formset = GenericFormSet(instance=platypus)
        tagged_item_id = TaggedItem.objects.get(tag='shiny', object_id=platypus.id).id
        self.assertHTMLEqual(
            ''.join(form.as_p() for form in formset.forms),
            """<p><label for="id_generic_relations-taggeditem-content_type-object_id-0-tag">Tag:</label>
<input id="id_generic_relations-taggeditem-content_type-object_id-0-tag" type="text"
name="generic_relations-taggeditem-content_type-object_id-0-tag" value="shiny" maxlength="50"></p>
<p><label for="id_generic_relations-taggeditem-content_type-object_id-0-DELETE">Delete:</label>
<input type="checkbox" name="generic_relations-taggeditem-content_type-object_id-0-DELETE"
id="id_generic_relations-taggeditem-content_type-object_id-0-DELETE">
<input type="hidden" name="generic_relations-taggeditem-content_type-object_id-0-id"
value="%s" id="id_generic_relations-taggeditem-content_type-object_id-0-id"></p>
<p><label for="id_generic_relations-taggeditem-content_type-object_id-1-tag">Tag:</label>
<input id="id_generic_relations-taggeditem-content_type-object_id-1-tag" type="text"
name="generic_relations-taggeditem-content_type-object_id-1-tag" maxlength="50"></p>
<p><label for="id_generic_relations-taggeditem-content_type-object_id-1-DELETE">Delete:</label>
<input type="checkbox" name="generic_relations-taggeditem-content_type-object_id-1-DELETE"
id="id_generic_relations-taggeditem-content_type-object_id-1-DELETE">
<input type="hidden" name="generic_relations-taggeditem-content_type-object_id-1-id"
id="id_generic_relations-taggeditem-content_type-object_id-1-id"></p>""" % tagged_item_id
        )
        lion = Animal.objects.create(common_name='Lion', latin_name='Panthera leo')
        formset = GenericFormSet(instance=lion, prefix='x')
        self.assertHTMLEqual(
            ''.join(form.as_p() for form in formset.forms),
            """<p><label for="id_x-0-tag">Tag:</label>
<input id="id_x-0-tag" type="text" name="x-0-tag" maxlength="50"></p>
<p><label for="id_x-0-DELETE">Delete:</label> <input type="checkbox" name="x-0-DELETE" id="id_x-0-DELETE">
<input type="hidden" name="x-0-id" id="id_x-0-id"></p>"""
        )

    def test_options(self):
        """
        Tests the behavior of the `TaggedItemFormSet` with different querysets and configurations.
        
        - Creates an instance of `TaggedItemFormSet` without a queryset and verifies the number of forms and initial data.
        - Uses a queryset to alter the display order of the forms.
        - Utilizes a queryset to filter out certain instances and checks the resulting formset length and content.
        """

        TaggedItemFormSet = generic_inlineformset_factory(
            TaggedItem,
            can_delete=False,
            exclude=['tag'],
            extra=3,
        )
        platypus = Animal.objects.create(common_name='Platypus', latin_name='Ornithorhynchus anatinus')
        harmless = platypus.tags.create(tag='harmless')
        mammal = platypus.tags.create(tag='mammal')
        # Works without a queryset.
        formset = TaggedItemFormSet(instance=platypus)
        self.assertEqual(len(formset.forms), 5)
        self.assertHTMLEqual(
            formset.forms[0].as_p(),
            '<input type="hidden" name="generic_relations-taggeditem-content_type-object_id-0-id" value="%s" '
            'id="id_generic_relations-taggeditem-content_type-object_id-0-id">' % harmless.pk
        )
        self.assertEqual(formset.forms[0].instance, harmless)
        self.assertEqual(formset.forms[1].instance, mammal)
        self.assertIsNone(formset.forms[2].instance.pk)
        # A queryset can be used to alter display ordering.
        formset = TaggedItemFormSet(instance=platypus, queryset=TaggedItem.objects.order_by('-tag'))
        self.assertEqual(len(formset.forms), 5)
        self.assertEqual(formset.forms[0].instance, mammal)
        self.assertEqual(formset.forms[1].instance, harmless)
        self.assertIsNone(formset.forms[2].instance.pk)
        # A queryset that omits items.
        formset = TaggedItemFormSet(instance=platypus, queryset=TaggedItem.objects.filter(tag__startswith='harm'))
        self.assertEqual(len(formset.forms), 4)
        self.assertEqual(formset.forms[0].instance, harmless)
        self.assertIsNone(formset.forms[1].instance.pk)

    def test_get_queryset_ordering(self):
        """
        BaseGenericInlineFormSet.get_queryset() adds default ordering, if
        needed.
        """
        inline_formset = generic_inlineformset_factory(TaggedItem, exclude=('tag',))
        formset = inline_formset(instance=Gecko.objects.create())
        self.assertIs(formset.get_queryset().ordered, True)

    def test_initial(self):
        """
        Test the initial data setup for a generic inline formset.
        
        This function creates an instance of the `Mineral` model with the name 'Quartz' and hardness 7. It then generates a `GenericFormSet` using `generic_inlineformset_factory` for the `TaggedItem` model with one extra form. The content type for the `Mineral` instance is retrieved using `ContentType.objects.get_for_model`. An initial data list is created containing a dictionary with tag 'l
        """

        quartz = Mineral.objects.create(name='Quartz', hardness=7)
        GenericFormSet = generic_inlineformset_factory(TaggedItem, extra=1)
        ctype = ContentType.objects.get_for_model(quartz)
        initial_data = [{
            'tag': 'lizard',
            'content_type': ctype.pk,
            'object_id': quartz.pk,
        }]
        formset = GenericFormSet(initial=initial_data)
        self.assertEqual(formset.forms[0].initial, initial_data[0])

    def test_meta_widgets(self):
        """TaggedItemForm has a widget defined in Meta."""
        Formset = generic_inlineformset_factory(TaggedItem, TaggedItemForm)
        form = Formset().forms[0]
        self.assertIsInstance(form['tag'].field.widget, CustomWidget)

    @isolate_apps('generic_relations')
    def test_incorrect_content_type(self):
        """
        Tests that an exception is raised when attempting to create a GenericInlineFormSet with a model that has a PositiveIntegerField instead of a ForeignKey to ContentType.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        Exception: If the provided model does not have a ForeignKey to ContentType.
        
        Important Functions:
        - `generic_inlineformset_factory`: Creates a formset for inline generic relations.
        - `self.assertRaisesMessage`: Asserts that a specific exception is raised with a given
        """

        class BadModel(models.Model):
            content_type = models.PositiveIntegerField()

        msg = "fk_name 'generic_relations.BadModel.content_type' is not a ForeignKey to ContentType"
        with self.assertRaisesMessage(Exception, msg):
            generic_inlineformset_factory(BadModel, TaggedItemForm)

    def test_save_new_uses_form_save(self):
        """
        Tests the behavior of saving a new object using a custom form save method.
        
        This function creates an instance of `ProxyRelatedModel`, initializes a formset with a custom form that overrides the `save` method to set `saved_by` attribute, and then saves the formset. The test verifies that the `saved_by` attribute is correctly set to 'custom method' after saving.
        
        Args:
        self: The test case instance.
        
        Returns:
        None
        
        Functions Used:
        """

        class SaveTestForm(forms.ModelForm):
            def save(self, *args, **kwargs):
                self.instance.saved_by = 'custom method'
                return super().save(*args, **kwargs)

        Formset = generic_inlineformset_factory(ForProxyModelModel, fields='__all__', form=SaveTestForm)
        instance = ProxyRelatedModel.objects.create()
        data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '',
            'form-0-title': 'foo',
        }
        formset = Formset(data, instance=instance, prefix='form')
        self.assertTrue(formset.is_valid())
        new_obj = formset.save()[0]
        self.assertEqual(new_obj.saved_by, 'custom method')

    def test_save_new_for_proxy(self):
        """
        Test saving a new instance using a generic inline formset for a proxy model.
        
        This function creates an instance of `ProxyRelatedModel`, initializes a formset
        with `ForProxyModelModel` model, and saves a new object associated with the instance.
        The formset is configured with all fields and set to allow additional forms.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `generic_inlineformset_factory`: Creates a formset factory for
        """

        Formset = generic_inlineformset_factory(ForProxyModelModel, fields='__all__', for_concrete_model=False)
        instance = ProxyRelatedModel.objects.create()
        data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '',
            'form-0-title': 'foo',
        }
        formset = Formset(data, instance=instance, prefix='form')
        self.assertTrue(formset.is_valid())
        new_obj, = formset.save()
        self.assertEqual(new_obj.obj, instance)

    def test_save_new_for_concrete(self):
        """
        Test saving a new object using a generic inline formset for a concrete model.
        
        This function creates an instance of `ProxyRelatedModel`, initializes a formset with specific data,
        validates the formset, and saves a new object. The test ensures that the saved object is not an instance
        of `ProxyRelatedModel`.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `generic_inlineformset_factory`: Creates a formset factory for inline forms
        """

        Formset = generic_inlineformset_factory(ForProxyModelModel, fields='__all__', for_concrete_model=True)
        instance = ProxyRelatedModel.objects.create()
        data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '',
            'form-0-title': 'foo',
        }
        formset = Formset(data, instance=instance, prefix='form')
        self.assertTrue(formset.is_valid())
        new_obj, = formset.save()
        self.assertNotIsInstance(new_obj.obj, ProxyRelatedModel)

    def test_initial_count(self):
        """
        Tests the initial form count for a generic inline formset.
        
        This function creates an instance of `GenericInlineFormSet` with initial
        form data and checks the initial form count. It also tests the behavior
        when the `save_as_new` parameter is set to `True`.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `generic_inlineformset_factory`: Creates a generic inline formset.
        - `GenericFormSet`: Represents the
        """

        GenericFormSet = generic_inlineformset_factory(TaggedItem)
        data = {
            'form-TOTAL_FORMS': '3',
            'form-INITIAL_FORMS': '3',
            'form-MAX_NUM_FORMS': '',
        }
        formset = GenericFormSet(data=data, prefix='form')
        self.assertEqual(formset.initial_form_count(), 3)
        formset = GenericFormSet(data=data, prefix='form', save_as_new=True)
        self.assertEqual(formset.initial_form_count(), 0)

    def test_save_as_new(self):
        """
        The save_as_new parameter creates new items that are associated with
        the object.
        """
        lion = Animal.objects.create(common_name='Lion', latin_name='Panthera leo')
        yellow = lion.tags.create(tag='yellow')
        hairy = lion.tags.create(tag='hairy')
        GenericFormSet = generic_inlineformset_factory(TaggedItem)
        data = {
            'form-TOTAL_FORMS': '3',
            'form-INITIAL_FORMS': '2',
            'form-MAX_NUM_FORMS': '',
            'form-0-id': str(yellow.pk),
            'form-0-tag': 'hunts',
            'form-1-id': str(hairy.pk),
            'form-1-tag': 'roars',
        }
        formset = GenericFormSet(data, instance=lion, prefix='form', save_as_new=True)
        self.assertTrue(formset.is_valid())
        tags = formset.save()
        self.assertEqual([tag.tag for tag in tags], ['hunts', 'roars'])
        hunts, roars = tags
        self.assertSequenceEqual(lion.tags.order_by('tag'), [hairy, hunts, roars, yellow])

    def test_absolute_max(self):
        """
        Tests the behavior of the `GenericFormSet` with an `absolute_max` constraint.
        
        This function creates a `GenericFormSet` using `generic_inlineformset_factory` with an `absolute_max` value of 1500. It then attempts to create a formset with 1501 forms by providing a data dictionary with `form-TOTAL_FORMS` set to 1501. The function checks if the formset is valid, the number of forms
        """

        GenericFormSet = generic_inlineformset_factory(TaggedItem, absolute_max=1500)
        data = {
            'form-TOTAL_FORMS': '1501',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '0',
        }
        formset = GenericFormSet(data=data, prefix='form')
        self.assertIs(formset.is_valid(), False)
        self.assertEqual(len(formset.forms), 1500)
        self.assertEqual(
            formset.non_form_errors(),
            ['Please submit at most 1000 forms.'],
        )

    def test_absolute_max_with_max_num(self):
        """
        Tests the behavior of the `GenericFormSet` with `max_num` and `absolute_max` set.
        
        This function creates an instance of `GenericFormSet` with `max_num` set to 20 and `absolute_max` set to 100. It then submits a POST request with 101 form instances. The function asserts that the formset is invalid due to exceeding the maximum number of forms allowed by `max_num`, but still allows up to 1
        """

        GenericFormSet = generic_inlineformset_factory(
            TaggedItem,
            max_num=20,
            absolute_max=100,
        )
        data = {
            'form-TOTAL_FORMS': '101',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '0',
        }
        formset = GenericFormSet(data=data, prefix='form')
        self.assertIs(formset.is_valid(), False)
        self.assertEqual(len(formset.forms), 100)
        self.assertEqual(
            formset.non_form_errors(),
            ['Please submit at most 20 forms.'],
        )

    def test_can_delete_extra(self):
        """
        Tests if a generic inline formset with `can_delete` and `can_delete_extra` set to True can be created and has the expected number of forms with delete fields.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `generic_inlineformset_factory`: Creates a formset factory for generic inline forms.
        - `can_delete`: Enables deletion of form instances.
        - `can_delete_extra`: Adds extra forms with delete fields.
        - `extra
        """

        GenericFormSet = generic_inlineformset_factory(
            TaggedItem,
            can_delete=True,
            can_delete_extra=True,
            extra=2,
        )
        formset = GenericFormSet()
        self.assertEqual(len(formset), 2)
        self.assertIn('DELETE', formset.forms[0].fields)
        self.assertIn('DELETE', formset.forms[1].fields)

    def test_disable_delete_extra(self):
        """
        Test disabling delete functionality for extra forms in a generic inline formset.
        
        This function creates a generic inline formset with `can_delete` set to True, `can_delete_extra` set to False, and `extra` set to 2. It then checks that the formset contains two forms and that the 'DELETE' field is not present in either of the forms.
        
        Args:
        None
        
        Returns:
        None
        """

        GenericFormSet = generic_inlineformset_factory(
            TaggedItem,
            can_delete=True,
            can_delete_extra=False,
            extra=2,
        )
        formset = GenericFormSet()
        self.assertEqual(len(formset), 2)
        self.assertNotIn('DELETE', formset.forms[0].fields)
        self.assertNotIn('DELETE', formset.forms[1].fields)
