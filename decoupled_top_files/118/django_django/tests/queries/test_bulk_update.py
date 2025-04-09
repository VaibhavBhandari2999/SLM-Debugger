import datetime

from django.core.exceptions import FieldDoesNotExist
from django.db.models import F
from django.db.models.functions import Lower
from django.db.utils import IntegrityError
from django.test import TestCase, override_settings, skipUnlessDBFeature

from .models import (
    Article,
    CustomDbColumn,
    CustomPk,
    Detail,
    Food,
    Individual,
    JSONFieldNullable,
    Member,
    Note,
    Number,
    Order,
    Paragraph,
    RelatedObject,
    SingleObject,
    SpecialCategory,
    Tag,
    Valid,
)


class WriteToOtherRouter:
    def db_for_write(self, model, **hints):
        return "other"


class BulkUpdateNoteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.notes = [Note.objects.create(note=str(i), misc=str(i)) for i in range(10)]

    def create_tags(self):
        self.tags = [Tag.objects.create(name=str(i)) for i in range(10)]

    def test_simple(self):
        """
        Test bulk updating of notes.
        
        This function updates the 'note' field of multiple notes using the `bulk_update` method,
        ensuring that only one database query is executed. It iterates through a list of notes,
        sets their 'note' field to a formatted string containing their ID, and then performs the
        bulk update operation. Finally, it verifies that the updated notes match the expected values
        by comparing the 'note' field values from the database with the expected values.
        """

        for note in self.notes:
            note.note = "test-%s" % note.id
        with self.assertNumQueries(1):
            Note.objects.bulk_update(self.notes, ["note"])
        self.assertCountEqual(
            Note.objects.values_list("note", flat=True),
            [cat.note for cat in self.notes],
        )

    def test_multiple_fields(self):
        """
        Test bulk updating multiple fields in a Note model using Django's bulk_update method.
        
        This function updates the 'note' and 'misc' fields of multiple Note objects in a single database query.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `Note.objects.bulk_update`: Updates multiple fields in a queryset of Note objects in a single database query.
        - `assertNumQueries`: Asserts that the number of database queries executed is as expected.
        -
        """

        for note in self.notes:
            note.note = "test-%s" % note.id
            note.misc = "misc-%s" % note.id
        with self.assertNumQueries(1):
            Note.objects.bulk_update(self.notes, ["note", "misc"])
        self.assertCountEqual(
            Note.objects.values_list("note", flat=True),
            [cat.note for cat in self.notes],
        )
        self.assertCountEqual(
            Note.objects.values_list("misc", flat=True),
            [cat.misc for cat in self.notes],
        )

    def test_batch_size(self):
        with self.assertNumQueries(len(self.notes)):
            Note.objects.bulk_update(self.notes, fields=["note"], batch_size=1)

    def test_unsaved_models(self):
        """
        Test that unsaved models cannot be bulk updated.
        
        This function checks if all objects intended for bulk update via
        `bulk_update()` have primary keys set. If any object lacks a primary key,
        a `ValueError` is raised with a specific message indicating the issue.
        
        Args:
        None (The test case method does not take any explicit arguments).
        
        Returns:
        None (The function raises an exception if the condition is not met).
        
        Raises:
        ValueError: If any
        """

        objs = self.notes + [Note(note="test", misc="test")]
        msg = "All bulk_update() objects must have a primary key set."
        with self.assertRaisesMessage(ValueError, msg):
            Note.objects.bulk_update(objs, fields=["note"])

    def test_foreign_keys_do_not_lookup(self):
        """
        Test that foreign key lookups are not performed during bulk update operations.
        
        This function creates tags and associates them with notes using a foreign key relationship. It then performs a bulk update on the notes without triggering additional database queries for foreign key lookups. The updated notes are verified to have non-null tags.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - create_tags: Creates and returns a list of tags.
        - zip: Zips notes and tags together
        """

        self.create_tags()
        for note, tag in zip(self.notes, self.tags):
            note.tag = tag
        with self.assertNumQueries(1):
            Note.objects.bulk_update(self.notes, ["tag"])
        self.assertSequenceEqual(Note.objects.filter(tag__isnull=False), self.notes)

    def test_set_field_to_null(self):
        """
        Sets the tag field of multiple notes to null.
        
        This function updates the tag field of all notes to None using bulk_update for efficiency. It first creates tags and notes, then updates the tag field of each note to None and finally asserts that all notes have a null tag.
        
        Functions Used:
        - create_tags: Creates tags for notes.
        - Note.objects.update: Updates the tag field of all notes to the specified tag.
        - Note.objects.bulk_update: Updates the tag field of
        """

        self.create_tags()
        Note.objects.update(tag=self.tags[0])
        for note in self.notes:
            note.tag = None
        Note.objects.bulk_update(self.notes, ["tag"])
        self.assertCountEqual(Note.objects.filter(tag__isnull=True), self.notes)

    def test_set_mixed_fields_to_null(self):
        """
        Sets mixed fields to null in a bulk update operation on Note objects.
        
        This function creates tags, splits notes into two groups, sets the tag field of the first group to None,
        and sets the tag field of the second group to a specific tag. It then performs a bulk update on the notes
        and asserts that the notes with null tags match the first group and those with non-null tags match the second group.
        
        Args:
        None
        
        Returns:
        None
        """

        self.create_tags()
        midpoint = len(self.notes) // 2
        top, bottom = self.notes[:midpoint], self.notes[midpoint:]
        for note in top:
            note.tag = None
        for note in bottom:
            note.tag = self.tags[0]
        Note.objects.bulk_update(self.notes, ["tag"])
        self.assertCountEqual(Note.objects.filter(tag__isnull=True), top)
        self.assertCountEqual(Note.objects.filter(tag__isnull=False), bottom)

    def test_functions(self):
        """
        Updates all notes to a specific value and then converts their content to lowercase.
        
        This function updates the `note` field of all `Note` objects to "TEST" using `Note.objects.update()`. It then iterates over a list of `notes`, converting each `note` to lowercase using `Lower("note")`. Finally, it bulk updates the `note` field of all `Note` objects with the modified list using `Note.objects.bulk_update()`. The function asserts that the
        """

        Note.objects.update(note="TEST")
        for note in self.notes:
            note.note = Lower("note")
        Note.objects.bulk_update(self.notes, ["note"])
        self.assertEqual(set(Note.objects.values_list("note", flat=True)), {"test"})

    # Tests that use self.notes go here, otherwise put them in another class.


class BulkUpdateTests(TestCase):
    databases = {"default", "other"}

    def test_no_fields(self):
        """
        Raise a ValueError if no field names are provided to bulk_update.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        ValueError: If no field names are provided to bulk_update.
        
        Notes:
        This function tests the behavior of the bulk_update method when no field names are specified. It asserts that a ValueError is raised with the message "Field names must be given to bulk_update()".
        """

        msg = "Field names must be given to bulk_update()."
        with self.assertRaisesMessage(ValueError, msg):
            Note.objects.bulk_update([], fields=[])

    def test_invalid_batch_size(self):
        """
        Test invalid batch sizes for bulk update operations.
        
        This function checks that an appropriate error message is raised when
        attempting to perform a bulk update with an invalid batch size. The
        expected error message is "Batch size must be a positive integer."
        
        Args:
        None
        
        Raises:
        ValueError: If the batch size is not a positive integer.
        
        Methods Used:
        - `Note.objects.bulk_update`: Performs the bulk update operation.
        - `self.assertRaisesMessage`: Asserts
        """

        msg = "Batch size must be a positive integer."
        with self.assertRaisesMessage(ValueError, msg):
            Note.objects.bulk_update([], fields=["note"], batch_size=-1)
        with self.assertRaisesMessage(ValueError, msg):
            Note.objects.bulk_update([], fields=["note"], batch_size=0)

    def test_nonexistent_field(self):
        """
        Test that bulk_update raises a FieldDoesNotExist error when attempting to update a non-existent field.
        
        This function checks if bulk_update on a Note model instance fails gracefully when provided with a non-existent field name. It uses `assertRaisesMessage` to verify that the expected exception is raised with the correct message.
        
        Args:
        None (This is a test method, so no arguments are passed).
        
        Raises:
        FieldDoesNotExist: If the Note model does not have a field named 'non
        """

        with self.assertRaisesMessage(
            FieldDoesNotExist, "Note has no field named 'nonexistent'"
        ):
            Note.objects.bulk_update([], ["nonexistent"])

    pk_fields_error = "bulk_update() cannot be used with primary key fields."

    def test_update_primary_key(self):
        with self.assertRaisesMessage(ValueError, self.pk_fields_error):
            Note.objects.bulk_update([], ["id"])

    def test_update_custom_primary_key(self):
        with self.assertRaisesMessage(ValueError, self.pk_fields_error):
            CustomPk.objects.bulk_update([], ["name"])

    def test_empty_objects(self):
        """
        Test the bulk update functionality with an empty list of objects.
        
        This test ensures that no database queries are executed when attempting
        to bulk update an empty list of Note objects. The `bulk_update` method is
        called with an empty list and the field 'note' to be updated. The number
        of rows updated is expected to be 0.
        
        Args:
        None
        
        Returns:
        None
        
        Raises:
        AssertionError: If the number of rows updated is not
        """

        with self.assertNumQueries(0):
            rows_updated = Note.objects.bulk_update([], ["note"])
        self.assertEqual(rows_updated, 0)

    def test_large_batch(self):
        """
        Bulk create and update a large batch of Note objects.
        
        This function creates a large batch of Note objects using `bulk_create` and then updates their 'note' field using `bulk_update`. The number of rows updated is verified to be equal to the number of created notes.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `Note.objects.bulk_create`: Creates a large batch of Note objects.
        - `Note.objects.bulk_update`: Updates the 'note
        """

        Note.objects.bulk_create(
            [Note(note=str(i), misc=str(i)) for i in range(0, 2000)]
        )
        notes = list(Note.objects.all())
        rows_updated = Note.objects.bulk_update(notes, ["note"])
        self.assertEqual(rows_updated, 2000)

    def test_updated_rows_when_passing_duplicates(self):
        """
        Updates multiple notes' 'note' field with a new value and returns the number of rows updated. The function demonstrates bulk updating with and without batch size.
        
        Args:
        None
        
        Returns:
        None
        
        Important Functions:
        - `Note.objects.bulk_update`: Updates multiple objects in a single database query.
        - `Note.objects.create`: Creates a new note object.
        
        Batch Size:
        - When no batch size is specified, the function updates the notes in one go and returns
        """

        note = Note.objects.create(note="test-note", misc="test")
        rows_updated = Note.objects.bulk_update([note, note], ["note"])
        self.assertEqual(rows_updated, 1)
        # Duplicates in different batches.
        rows_updated = Note.objects.bulk_update([note, note], ["note"], batch_size=1)
        self.assertEqual(rows_updated, 2)

    def test_only_concrete_fields_allowed(self):
        """
        Test that bulk_update() can only be used with concrete fields.
        
        This function creates instances of `Valid`, `Detail`, and `Paragraph` models,
        and attempts to use `bulk_update()` on the `Detail` and `Paragraph` objects
        with non-concrete fields (`member` and `page`). It asserts that a `ValueError`
        is raised with the message "bulk_update() can only be used with concrete fields."
        
        - `Valid`: Model instance created with `
        """

        obj = Valid.objects.create(valid="test")
        detail = Detail.objects.create(data="test")
        paragraph = Paragraph.objects.create(text="test")
        Member.objects.create(name="test", details=detail)
        msg = "bulk_update() can only be used with concrete fields."
        with self.assertRaisesMessage(ValueError, msg):
            Detail.objects.bulk_update([detail], fields=["member"])
        with self.assertRaisesMessage(ValueError, msg):
            Paragraph.objects.bulk_update([paragraph], fields=["page"])
        with self.assertRaisesMessage(ValueError, msg):
            Valid.objects.bulk_update([obj], fields=["parent"])

    def test_custom_db_columns(self):
        """
        Tests the behavior of bulk updating a custom database column.
        
        This function creates an instance of `CustomDbColumn` with a custom column value of 1,
        updates the custom column value to 2, performs a bulk update on the model using the
        `bulk_update` method, refreshes the model from the database, and asserts that the
        custom column value is now 2.
        
        Functions Used:
        - `CustomDbColumn.objects.create()`: Creates a new instance of
        """

        model = CustomDbColumn.objects.create(custom_column=1)
        model.custom_column = 2
        CustomDbColumn.objects.bulk_update([model], fields=["custom_column"])
        model.refresh_from_db()
        self.assertEqual(model.custom_column, 2)

    def test_custom_pk(self):
        """
        Tests the behavior of `CustomPk` model's `extra` field after bulk updating.
        
        This function creates 10 instances of `CustomPk` with unique names and empty `extra` fields. It then updates the `extra` field for each instance with a value based on its primary key. Finally, it uses `bulk_update` to efficiently update all instances at once and asserts that the updated `extra` values match the expected values.
        
        :param self: The current test case instance
        """

        custom_pks = [
            CustomPk.objects.create(name="pk-%s" % i, extra="") for i in range(10)
        ]
        for model in custom_pks:
            model.extra = "extra-%s" % model.pk
        CustomPk.objects.bulk_update(custom_pks, ["extra"])
        self.assertCountEqual(
            CustomPk.objects.values_list("extra", flat=True),
            [cat.extra for cat in custom_pks],
        )

    def test_falsey_pk_value(self):
        """
        Tests the behavior of updating an order with a falsey primary key value using bulk_update.
        
        This function creates an order instance with a primary key of 0, updates its name,
        and then uses bulk_update to modify the name field. After refreshing the order from
        the database, it asserts that the updated name is 'updated'.
        
        :param None: No input parameters are required for this function.
        :return: None. The function asserts the expected outcome.
        """

        order = Order.objects.create(pk=0, name="test")
        order.name = "updated"
        Order.objects.bulk_update([order], ["name"])
        order.refresh_from_db()
        self.assertEqual(order.name, "updated")

    def test_inherited_fields(self):
        """
        Tests the behavior of inherited fields in SpecialCategory model.
        
        This function creates instances of SpecialCategory, updates their names and special_names,
        and then verifies that the updated values are correctly stored in the database.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - SpecialCategory.objects.create: Creates new instances of SpecialCategory.
        - SpecialCategory.objects.bulk_update: Updates multiple fields of existing SpecialCategory instances.
        - assertCountEqual: Compares the expected and
        """

        special_categories = [
            SpecialCategory.objects.create(name=str(i), special_name=str(i))
            for i in range(10)
        ]
        for category in special_categories:
            category.name = "test-%s" % category.id
            category.special_name = "special-test-%s" % category.special_name
        SpecialCategory.objects.bulk_update(
            special_categories, ["name", "special_name"]
        )
        self.assertCountEqual(
            SpecialCategory.objects.values_list("name", flat=True),
            [cat.name for cat in special_categories],
        )
        self.assertCountEqual(
            SpecialCategory.objects.values_list("special_name", flat=True),
            [cat.special_name for cat in special_categories],
        )

    def test_field_references(self):
        """
        Tests the functionality of field references in bulk updates.
        
        This test creates a list of 10 Number objects with initial num value of 0.
        It then increments the num value of each object by 1 using a field reference (F("num") + 1).
        After updating the objects in bulk, it verifies that all objects have their num value set to 1.
        """

        numbers = [Number.objects.create(num=0) for _ in range(10)]
        for number in numbers:
            number.num = F("num") + 1
        Number.objects.bulk_update(numbers, ["num"])
        self.assertCountEqual(Number.objects.filter(num=1), numbers)

    def test_f_expression(self):
        """
        Tests updating the 'misc' field of multiple notes using F expressions.
        
        This function creates 10 notes with a 'note' and 'misc' field, then updates
        the 'misc' field of each note to be equal to its corresponding 'note' field.
        The changes are then bulk updated in the database. The function asserts that
        all notes have their 'misc' field set to the value of their 'note' field.
        
        Args:
        None
        
        Returns
        """

        notes = [
            Note.objects.create(note="test_note", misc="test_misc") for _ in range(10)
        ]
        for note in notes:
            note.misc = F("note")
        Note.objects.bulk_update(notes, ["misc"])
        self.assertCountEqual(Note.objects.filter(misc="test_note"), notes)

    def test_booleanfield(self):
        """
        Tests the behavior of updating a BooleanField in a Django model using bulk update.
        
        This function creates a list of 10 `Individual` objects with the `alive` field set to False,
        then updates the `alive` field to True for each object. The changes are then applied in bulk
        using `bulk_update`. Finally, it asserts that all `Individual` objects in the database have
        their `alive` field set to True.
        
        - Individuals: A list of
        """

        individuals = [Individual.objects.create(alive=False) for _ in range(10)]
        for individual in individuals:
            individual.alive = True
        Individual.objects.bulk_update(individuals, ["alive"])
        self.assertCountEqual(Individual.objects.filter(alive=True), individuals)

    def test_ipaddressfield(self):
        """
        Tests the behavior of the `CustomDbColumn` model's `ip_address` field when using `bulk_update`.
        
        This function iterates over a list of IP addresses (`"2001::1"` and `"1.2.3.4"`),
        creates instances of `CustomDbColumn` with an initial `ip_address` value of `"0.0.0.0"`,
        updates their `ip_address` to the current IP address in the loop,
        performs
        """

        for ip in ("2001::1", "1.2.3.4"):
            with self.subTest(ip=ip):
                models = [
                    CustomDbColumn.objects.create(ip_address="0.0.0.0")
                    for _ in range(10)
                ]
                for model in models:
                    model.ip_address = ip
                CustomDbColumn.objects.bulk_update(models, ["ip_address"])
                self.assertCountEqual(
                    CustomDbColumn.objects.filter(ip_address=ip), models
                )

    def test_datetime_field(self):
        """
        Tests the behavior of updating a `datetime` field using `bulk_update`.
        
        This function creates a list of `Article` objects with their `created` fields set to the current date and time. It then updates all these articles to have the same `created` field value, `point_in_time`, using `bulk_update`. Finally, it asserts that all articles now have the `created` field set to `point_in_time`.
        
        :param None: No parameters are passed directly to this
        """

        articles = [
            Article.objects.create(name=str(i), created=datetime.datetime.today())
            for i in range(10)
        ]
        point_in_time = datetime.datetime(1991, 10, 31)
        for article in articles:
            article.created = point_in_time
        Article.objects.bulk_update(articles, ["created"])
        self.assertCountEqual(Article.objects.filter(created=point_in_time), articles)

    @skipUnlessDBFeature("supports_json_field")
    def test_json_field(self):
        """
        Tests the behavior of a JSONField with bulk updates. Creates instances of JSONFieldNullable with integer values, updates their JSON fields, and verifies that the updated fields are present.
        
        - **Important Functions**: `bulk_create`, `bulk_update`, `filter`
        - **Key Variables**: `JSONFieldNullable`, `json_field`
        """

        JSONFieldNullable.objects.bulk_create(
            [JSONFieldNullable(json_field={"a": i}) for i in range(10)]
        )
        objs = JSONFieldNullable.objects.all()
        for obj in objs:
            obj.json_field = {"c": obj.json_field["a"] + 1}
        JSONFieldNullable.objects.bulk_update(objs, ["json_field"])
        self.assertCountEqual(
            JSONFieldNullable.objects.filter(json_field__has_key="c"), objs
        )

    def test_nullable_fk_after_related_save(self):
        """
        Tests the behavior of nullable foreign key relationships after saving related objects.
        
        This function creates a `RelatedObject` instance and associates it with a `SingleObject` instance. It then saves the `SingleObject`, performs a bulk update on the `RelatedObject`, and verifies that the foreign key relationship is correctly maintained.
        
        Args:
        None
        
        Returns:
        None
        
        Functions Used:
        - `RelatedObject.objects.create()`: Creates a new `RelatedObject` instance.
        - `
        """

        parent = RelatedObject.objects.create()
        child = SingleObject()
        parent.single = child
        parent.single.save()
        RelatedObject.objects.bulk_update([parent], fields=["single"])
        self.assertEqual(parent.single_id, parent.single.pk)
        parent.refresh_from_db()
        self.assertEqual(parent.single, child)

    def test_unsaved_parent(self):
        """
        Raises a ValueError when attempting to bulk update a related object that is not saved, to prevent data loss.
        
        Args:
        None (The function uses instance variables within its scope).
        
        Returns:
        None (Raises an exception if the bulk update operation is attempted).
        
        Important Functions:
        - `RelatedObject.objects.create()`: Creates a new instance of `RelatedObject`.
        - `RelatedObject.objects.bulk_update()`: Attempts to perform a bulk update on the `RelatedObject` instances.
        """

        parent = RelatedObject.objects.create()
        parent.single = SingleObject()
        msg = (
            "bulk_update() prohibited to prevent data loss due to unsaved "
            "related object 'single'."
        )
        with self.assertRaisesMessage(ValueError, msg):
            RelatedObject.objects.bulk_update([parent], fields=["single"])

    def test_unspecified_unsaved_parent(self):
        """
        Tests bulk updating of a related object without specifying the parent.
        Creates a RelatedObject instance, sets its single field to a new SingleObject instance, and updates the 'f' field using bulk_update. The parent is not explicitly saved or specified during the update process. After refreshing the parent from the database, the 'f' field should retain its updated value, while the 'single' field should be None.
        """

        parent = RelatedObject.objects.create()
        parent.single = SingleObject()
        parent.f = 42
        RelatedObject.objects.bulk_update([parent], fields=["f"])
        parent.refresh_from_db()
        self.assertEqual(parent.f, 42)
        self.assertIsNone(parent.single)

    @override_settings(DATABASE_ROUTERS=[WriteToOtherRouter()])
    def test_database_routing(self):
        """
        Tests database routing for bulk update operations.
        
        This function creates a new note object, updates its note field, and then performs a bulk update operation on the note object using the 'other' database. The assertNumQueries context manager is used to ensure that only one query is executed against the 'other' database during the bulk update operation.
        
        :param self: The instance of the class containing this method.
        :type self: object
        :return: None
        :rtype: None
        """

        note = Note.objects.create(note="create")
        note.note = "bulk_update"
        with self.assertNumQueries(1, using="other"):
            Note.objects.bulk_update([note], fields=["note"])

    @override_settings(DATABASE_ROUTERS=[WriteToOtherRouter()])
    def test_database_routing_batch_atomicity(self):
        """
        Tests the atomicity of database routing during a batch update operation.
        
        This function creates two instances of the `Food` model, updates their names,
        and attempts to perform a batch update using `bulk_update`. The operation is
        wrapped in a transaction that should roll back if an `IntegrityError` occurs.
        The function asserts that no records with the name 'Kiwi' exist after the
        operation, indicating proper rollback behavior.
        
        - `Food.objects.create`: Creates new
        """

        f1 = Food.objects.create(name="Banana")
        f2 = Food.objects.create(name="Apple")
        f1.name = "Kiwi"
        f2.name = "Kiwi"
        with self.assertRaises(IntegrityError):
            Food.objects.bulk_update([f1, f2], fields=["name"], batch_size=1)
        self.assertIs(Food.objects.filter(name="Kiwi").exists(), False)
