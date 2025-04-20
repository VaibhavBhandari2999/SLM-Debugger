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
        This function tests the output of a generic inline formset for a model with a many-to-many relationship through a through model.
        
        Key Parameters:
        - None
        
        Key Keywords:
        - None
        
        Input:
        - None
        
        Output:
        - The function asserts the HTML output of the formset for different scenarios, including:
        - An empty formset
        - A formset with an instance
        - A formset with an instance that already has related objects
        - A formset with a different prefix
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
        Tests the function `generic_inlineformset_factory` with an incorrect content type field.
        
        This function checks if the `generic_inlineformset_factory` raises an exception when the content type field is not a ForeignKey to `ContentType`.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Raises:
        - Exception: If the `generic_inlineformset_factory` does not raise an exception when the content type field is not a ForeignKey to `ContentType`.
        
        Key Points:
        - A model `BadModel` is defined with
        """

        class BadModel(models.Model):
            content_type = models.PositiveIntegerField()

        msg = "fk_name 'generic_relations.BadModel.content_type' is not a ForeignKey to ContentType"
        with self.assertRaisesMessage(Exception, msg):
            generic_inlineformset_factory(BadModel, TaggedItemForm)

    def test_save_new_uses_form_save(self):
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
        
        Parameters:
        data (dict): A dictionary containing form data, including 'form-TOTAL_FORMS', 'form-INITIAL_FORMS', and 'form-MAX_NUM_FORMS'.
        save_as_new (bool): A flag indicating whether to save the form as new. Default is False.
        
        Returns:
        None: This function does not return anything. It asserts the initial form count of the formset.
        
        Key Steps:
        1.
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
        Test the behavior of a generic inline formset with absolute_max and max_num constraints.
        
        This function checks the validation and formset behavior when the number of forms submitted exceeds the max_num and absolute_max constraints.
        
        Parameters:
        - None (The function uses internal data and formset creation for testing)
        
        Returns:
        - None (The function asserts the validity and form count of the formset)
        
        Key Points:
        - max_num: The maximum number of forms allowed in the formset.
        - absolute_max: The maximum
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
        Test the disable_delete_extra functionality.
        
        This function creates a generic inline formset with the following parameters:
        - Model: TaggedItem
        - can_delete: True
        - can_delete_extra: False
        - extra: 2
        
        The function asserts that the formset contains exactly 2 forms and that the 'DELETE' field is not present in the first and second forms.
        
        Parameters:
        - None
        
        Returns:
        - None
        
        Key Assertions:
        - The formset contains exactly 2 forms.
        - The
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
