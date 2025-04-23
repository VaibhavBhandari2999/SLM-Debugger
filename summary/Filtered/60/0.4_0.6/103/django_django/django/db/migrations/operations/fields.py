from django.db.migrations.utils import field_references
from django.db.models import NOT_PROVIDED
from django.utils.functional import cached_property

from .base import Operation


class FieldOperation(Operation):
    def __init__(self, model_name, name, field=None):
        self.model_name = model_name
        self.name = name
        self.field = field

    @cached_property
    def model_name_lower(self):
        return self.model_name.lower()

    @cached_property
    def name_lower(self):
        return self.name.lower()

    def is_same_model_operation(self, operation):
        return self.model_name_lower == operation.model_name_lower

    def is_same_field_operation(self, operation):
        return (
            self.is_same_model_operation(operation)
            and self.name_lower == operation.name_lower
        )

    def references_model(self, name, app_label):
        """
        Determine if a model references another model.
        
        This function checks if a given model references another model by name.
        
        Parameters:
        name (str): The name of the model to check against.
        app_label (str): The application label of the model to check against.
        
        Returns:
        bool: True if the model references the given model, False otherwise.
        
        Key Considerations:
        - The function compares the provided model name and app label with the current model's name and app label.
        - If a field
        """

        name_lower = name.lower()
        if name_lower == self.model_name_lower:
            return True
        if self.field:
            return bool(
                field_references(
                    (app_label, self.model_name_lower),
                    self.field,
                    (app_label, name_lower),
                )
            )
        return False

    def references_field(self, model_name, name, app_label):
        model_name_lower = model_name.lower()
        # Check if this operation locally references the field.
        if model_name_lower == self.model_name_lower:
            if name == self.name:
                return True
            elif (
                self.field
                and hasattr(self.field, "from_fields")
                and name in self.field.from_fields
            ):
                return True
        # Check if this operation remotely references the field.
        if self.field is None:
            return False
        return bool(
            field_references(
                (app_label, self.model_name_lower),
                self.field,
                (app_label, model_name_lower),
                name,
            )
        )

    def reduce(self, operation, app_label):
        return super().reduce(operation, app_label) or not operation.references_field(
            self.model_name, self.name, app_label
        )


class AddField(FieldOperation):
    """Add a field to a model."""

    def __init__(self, model_name, name, field, preserve_default=True):
        self.preserve_default = preserve_default
        super().__init__(model_name, name, field)

    def deconstruct(self):
        kwargs = {
            "model_name": self.model_name,
            "name": self.name,
            "field": self.field,
        }
        if self.preserve_default is not True:
            kwargs["preserve_default"] = self.preserve_default
        return (self.__class__.__name__, [], kwargs)

    def state_forwards(self, app_label, state):
        """
        Add a field to a Django model state.
        
        This function adds a field to the specified model state for a given app label.
        
        Parameters:
        app_label (str): The label of the Django app containing the model.
        state (ModelState): The current state of the Django model.
        
        Key Parameters:
        app_label (str): The name of the Django app.
        state (ModelState): The current state of the model.
        
        Keywords:
        model_name_lower (str): The lowercase name of the model.
        """

        state.add_field(
            app_label,
            self.model_name_lower,
            self.name,
            self.field,
            self.preserve_default,
        )

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        to_model = to_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, to_model):
            from_model = from_state.apps.get_model(app_label, self.model_name)
            field = to_model._meta.get_field(self.name)
            if not self.preserve_default:
                field.default = self.field.default
            schema_editor.add_field(
                from_model,
                field,
            )
            if not self.preserve_default:
                field.default = NOT_PROVIDED

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        from_model = from_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, from_model):
            schema_editor.remove_field(
                from_model, from_model._meta.get_field(self.name)
            )

    def describe(self):
        return "Add field %s to %s" % (self.name, self.model_name)

    @property
    def migration_name_fragment(self):
        return "%s_%s" % (self.model_name_lower, self.name_lower)

    def reduce(self, operation, app_label):
        if isinstance(operation, FieldOperation) and self.is_same_field_operation(
            operation
        ):
            if isinstance(operation, AlterField):
                return [
                    AddField(
                        model_name=self.model_name,
                        name=operation.name,
                        field=operation.field,
                    ),
                ]
            elif isinstance(operation, RemoveField):
                return []
            elif isinstance(operation, RenameField):
                return [
                    AddField(
                        model_name=self.model_name,
                        name=operation.new_name,
                        field=self.field,
                    ),
                ]
        return super().reduce(operation, app_label)


class RemoveField(FieldOperation):
    """Remove a field from a model."""

    def deconstruct(self):
        kwargs = {
            "model_name": self.model_name,
            "name": self.name,
        }
        return (self.__class__.__name__, [], kwargs)

    def state_forwards(self, app_label, state):
        state.remove_field(app_label, self.model_name_lower, self.name)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """
        Remove a field from a model in the database.
        
        This function is used to remove a field from a model in the database. It is typically part of a database migration process.
        
        Parameters:
        app_label (str): The label of the Django app containing the model.
        schema_editor (django.db.backends.base.schema.BaseSchemaEditor): The schema editor object used to make changes to the database schema.
        from_state (ModelState): The current state of the model before the migration.
        to_state (ModelState
        """

        from_model = from_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, from_model):
            schema_editor.remove_field(
                from_model, from_model._meta.get_field(self.name)
            )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        """
        Method to add a field to a model in a backwards migration.
        
        Parameters:
        - app_label (str): The label of the Django application containing the model.
        - schema_editor (SchemaEditor): The schema editor object used to perform database operations.
        - from_state (ModelState): The state of the model before the migration.
        - to_state (ModelState): The state of the model after the migration.
        
        Key Parameters:
        - app_label: The name of the Django application.
        - schema_editor: The editor used
        """

        to_model = to_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, to_model):
            from_model = from_state.apps.get_model(app_label, self.model_name)
            schema_editor.add_field(from_model, to_model._meta.get_field(self.name))

    def describe(self):
        return "Remove field %s from %s" % (self.name, self.model_name)

    @property
    def migration_name_fragment(self):
        return "remove_%s_%s" % (self.model_name_lower, self.name_lower)

    def reduce(self, operation, app_label):
        from .models import DeleteModel

        if (
            isinstance(operation, DeleteModel)
            and operation.name_lower == self.model_name_lower
        ):
            return [operation]
        return super().reduce(operation, app_label)


class AlterField(FieldOperation):
    """
    Alter a field's database column (e.g. null, max_length) to the provided
    new field.
    """

    def __init__(self, model_name, name, field, preserve_default=True):
        self.preserve_default = preserve_default
        super().__init__(model_name, name, field)

    def deconstruct(self):
        kwargs = {
            "model_name": self.model_name,
            "name": self.name,
            "field": self.field,
        }
        if self.preserve_default is not True:
            kwargs["preserve_default"] = self.preserve_default
        return (self.__class__.__name__, [], kwargs)

    def state_forwards(self, app_label, state):
        state.alter_field(
            app_label,
            self.model_name_lower,
            self.name,
            self.field,
            self.preserve_default,
        )

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        to_model = to_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, to_model):
            from_model = from_state.apps.get_model(app_label, self.model_name)
            from_field = from_model._meta.get_field(self.name)
            to_field = to_model._meta.get_field(self.name)
            if not self.preserve_default:
                to_field.default = self.field.default
            schema_editor.alter_field(from_model, from_field, to_field)
            if not self.preserve_default:
                to_field.default = NOT_PROVIDED

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        self.database_forwards(app_label, schema_editor, from_state, to_state)

    def describe(self):
        return "Alter field %s on %s" % (self.name, self.model_name)

    @property
    def migration_name_fragment(self):
        return "alter_%s_%s" % (self.model_name_lower, self.name_lower)

    def reduce(self, operation, app_label):
        if isinstance(operation, RemoveField) and self.is_same_field_operation(
            operation
        ):
            return [operation]
        elif (
            isinstance(operation, RenameField)
            and self.is_same_field_operation(operation)
            and self.field.db_column is None
        ):
            return [
                operation,
                AlterField(
                    model_name=self.model_name,
                    name=operation.new_name,
                    field=self.field,
                ),
            ]
        return super().reduce(operation, app_label)


class RenameField(FieldOperation):
    """Rename a field on the model. Might affect db_column too."""

    def __init__(self, model_name, old_name, new_name):
        self.old_name = old_name
        self.new_name = new_name
        super().__init__(model_name, old_name)

    @cached_property
    def old_name_lower(self):
        return self.old_name.lower()

    @cached_property
    def new_name_lower(self):
        return self.new_name.lower()

    def deconstruct(self):
        kwargs = {
            "model_name": self.model_name,
            "old_name": self.old_name,
            "new_name": self.new_name,
        }
        return (self.__class__.__name__, [], kwargs)

    def state_forwards(self, app_label, state):
        state.rename_field(
            app_label, self.model_name_lower, self.old_name, self.new_name
        )

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        to_model = to_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, to_model):
            from_model = from_state.apps.get_model(app_label, self.model_name)
            schema_editor.alter_field(
                from_model,
                from_model._meta.get_field(self.old_name),
                to_model._meta.get_field(self.new_name),
            )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        to_model = to_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, to_model):
            from_model = from_state.apps.get_model(app_label, self.model_name)
            schema_editor.alter_field(
                from_model,
                from_model._meta.get_field(self.new_name),
                to_model._meta.get_field(self.old_name),
            )

    def describe(self):
        return "Rename field %s on %s to %s" % (
            self.old_name,
            self.model_name,
            self.new_name,
        )

    @property
    def migration_name_fragment(self):
        return "rename_%s_%s_%s" % (
            self.old_name_lower,
            self.model_name_lower,
            self.new_name_lower,
        )

    def references_field(self, model_name, name, app_label):
        return self.references_model(model_name, app_label) and (
            name.lower() == self.old_name_lower or name.lower() == self.new_name_lower
        )

    def reduce(self, operation, app_label):
        if (
            isinstance(operation, RenameField)
            and self.is_same_model_operation(operation)
            and self.new_name_lower == operation.old_name_lower
        ):
            return [
                RenameField(
                    self.model_name,
                    self.old_name,
                    operation.new_name,
                ),
            ]
        # Skip `FieldOperation.reduce` as we want to run `references_field`
        # against self.old_name and self.new_name.
        return super(FieldOperation, self).reduce(operation, app_label) or not (
            operation.references_field(self.model_name, self.old_name, app_label)
            or operation.references_field(self.model_name, self.new_name, app_label)
        )
   ]
        # Skip `FieldOperation.reduce` as we want to run `references_field`
        # against self.old_name and self.new_name.
        return super(FieldOperation, self).reduce(operation, app_label) or not (
            operation.references_field(self.model_name, self.old_name, app_label)
            or operation.references_field(self.model_name, self.new_name, app_label)
        )
