from django.db.migrations.utils import field_references
from django.db.models import NOT_PROVIDED
from django.utils.functional import cached_property

from .base import Operation


class FieldOperation(Operation):
    def __init__(self, model_name, name, field=None):
        """
        Initialize a new instance of the class.
        
        Args:
        model_name (str): The name of the model.
        name (str): The name of the instance.
        field (str, optional): The field associated with the instance. Defaults to None.
        
        Attributes:
        model_name (str): The name of the model.
        name (str): The name of the instance.
        field (str, optional): The field associated with the instance. Defaults to None.
        """

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
        """
        Determines if the given operation is a field-level operation on the same model.
        
        Args:
        operation (Operation): The operation to compare against.
        
        Returns:
        bool: True if the operation is on the same model and affects the same field, False otherwise.
        
        This method checks if the provided operation is of the same model and if it operates on the same field as the current instance. It uses the `is_same_model_operation` method to verify the model compatibility and compares the names of
        """

        return (
            self.is_same_model_operation(operation)
            and self.name_lower == operation.name_lower
        )

    def references_model(self, name, app_label):
        """
        Determines if a given model references the current model.
        
        Args:
        name (str): The name of the model to check.
        app_label (str): The application label of the model to check.
        
        Returns:
        bool: True if the given model references the current model, False otherwise.
        
        Important Functions:
        - `field_references`: Checks if a specific field references another model.
        - `name.lower()`: Converts the model name to lowercase for comparison.
        - `(app
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
        """
        Determines if the given model field references the current field.
        
        Args:
        model_name (str): The name of the model being checked.
        name (str): The name of the field being checked.
        app_label (str): The application label of the model being checked.
        
        Returns:
        bool: True if the given model field references the current field, False otherwise.
        
        Important Functions:
        - `model_name_lower`: Converts the model name to lowercase for comparison.
        - `
        """

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
        """
        Reduces the given operation based on whether it references a specific field.
        
        Args:
        operation (Operation): The operation to be reduced.
        app_label (str): The label of the application containing the model.
        
        Returns:
        bool: True if the operation does not reference the specified field, otherwise False.
        """

        return super().reduce(operation, app_label) or not operation.references_field(
            self.model_name, self.name, app_label
        )


class AddField(FieldOperation):
    """Add a field to a model."""

    def __init__(self, model_name, name, field, preserve_default=True):
        self.preserve_default = preserve_default
        super().__init__(model_name, name, field)

    def deconstruct(self):
        """
        Deconstructs the object into a tuple containing the class name, an empty list of positional arguments, and a dictionary of keyword arguments.
        
        Args:
        self: The instance of the class being deconstructed.
        
        Returns:
        A tuple with three elements:
        - The class name (`str`) of the instance being deconstructed.
        - An empty list (`list`) of positional arguments.
        - A dictionary (`dict`) of keyword arguments, containing:
        - `model_name` (`str
        """

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
        Adds a field to the given state for the specified model and field name.
        
        Args:
        app_label (str): The label of the Django application containing the model.
        state (MigrationState): The current state of the migration.
        
        This method modifies the `state` object by adding a new field to the specified model within the given application label. The field details are provided through the `self` object, which contains information about the field to be added (e.g., `model_name_lower
        """

        state.add_field(
            app_label,
            self.model_name_lower,
            self.name,
            self.field,
            self.preserve_default,
        )

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """
        Add a new field to an existing model in the database.
        
        Args:
        app_label (str): The label of the Django application containing the model.
        schema_editor: An instance of the schema editor used to perform database operations.
        from_state: The current state of the application's models.
        to_state: The target state of the application's models after the migration.
        
        This function adds a new field to an existing model in the database. It retrieves the target model using `to_state
        """

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
        """
        Removes a field from a model in the specified app label.
        
        Args:
        app_label (str): The name of the Django app containing the model.
        schema_editor: An instance of SchemaEditor used to perform the database operations.
        from_state: The current state of the application's models.
        to_state: The target state of the application's models after the operation.
        
        Returns:
        None
        
        Effects:
        - Removes a field from the specified model in the given app label
        """

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
        """
        Reduces a given operation to a set of operations that can be applied to the model.
        
        Args:
        operation (FieldOperation): The operation to be reduced.
        app_label (str): The application label of the model.
        
        Returns:
        list: A list of operations that can be applied to the model.
        
        Summary:
        This method processes a given `FieldOperation` and returns a list of operations based on the type of the operation. It checks if the operation is of type `
        """

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
        """
        Deconstructs the object into its constituent parts.
        
        Args:
        None
        
        Returns:
        A tuple containing the class name, an empty list, and a dictionary of keyword arguments.
        
        Keyword Arguments:
        model_name (str): The name of the model.
        name (str): The name of the object.
        """

        kwargs = {
            "model_name": self.model_name,
            "name": self.name,
        }
        return (self.__class__.__name__, [], kwargs)

    def state_forwards(self, app_label, state):
        state.remove_field(app_label, self.model_name_lower, self.name)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """
        Removes a field from a model in the database.
        
        Args:
        app_label (str): The label of the Django application containing the model.
        schema_editor: The schema editor object used to perform database operations.
        from_state: The current state of the application's models.
        to_state: The target state of the application's models after the operation.
        
        Summary:
        This function removes a specified field from a model in the database by using the schema editor to delete the field. It
        """

        from_model = from_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, from_model):
            schema_editor.remove_field(
                from_model, from_model._meta.get_field(self.name)
            )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        """
        Reverses the migration by adding a field to the existing model.
        
        Args:
        app_label (str): The label of the Django application containing the model.
        schema_editor: The schema editor object used to perform database operations.
        from_state: The state before the migration was applied.
        to_state: The state after the migration was applied.
        
        Returns:
        None
        
        This function reverses the migration by adding a field to the existing model. It retrieves the model from the target
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
        """
        Reduces the given operation based on the provided app label.
        
        Args:
        operation (DeleteModel): The operation to be reduced.
        app_label (str): The application label.
        
        Returns:
        list: A list containing the reduced operation or an empty list if no reduction is applicable.
        
        Notes:
        - This method checks if the operation is an instance of `DeleteModel` and if its name matches the model's lowercased name.
        - If the condition is met, it returns
        """

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
        """
        Deconstructs the object into a tuple containing the class name, an empty list of positional arguments, and a dictionary of keyword arguments.
        
        Args:
        self: The instance of the class being deconstructed.
        
        Returns:
        A tuple with three elements:
        - The class name (`str`) of the instance being deconstructed.
        - An empty list (`list`) of positional arguments.
        - A dictionary (`dict`) of keyword arguments, containing:
        - `model_name` (`str
        """

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
        Alters a field in a Django model's state. Modifies the given state object by applying changes to a specific field within a model defined by `app_label` and `model_name_lower`. The function uses the `alter_field` method of the `state` object to update the field named `self.name` with the new configuration specified by `self.field`.
        
        Args:
        app_label (str): The application label of the Django app containing the model.
        state (ModelState): The state
        """

        state.alter_field(
            app_label,
            self.model_name_lower,
            self.name,
            self.field,
            self.preserve_default,
        )

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """
        Alters an existing field in a Django model.
        
        Args:
        app_label (str): The label of the Django app containing the model.
        schema_editor: An instance of the schema editor class.
        from_state: The current state of the application's models.
        to_state: The target state of the application's models.
        
        This function alters an existing field in a Django model by updating its configuration. It retrieves the model and field information from both the current and target states, updates the
        """

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
        """
        Reduces a given operation by either returning the operation itself or a list of operations, depending on the type of the operation and the field's properties.
        
        Args:
        operation (Operation): The operation to be reduced.
        app_label (str): The application label.
        
        Returns:
        list[Operation] | Operation: A list of operations or a single operation based on the conditions met.
        
        Important Functions:
        - `is_same_field_operation`: Determines if the operation is the same as the
        """

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
        """
        Initialize a new instance of the class with the given `model_name`, `old_name`, and `new_name`.
        
        Args:
        model_name (str): The name of the model.
        old_name (str): The name of the old entity.
        new_name (str): The name of the new entity.
        
        Attributes:
        old_name (str): The name of the old entity.
        new_name (str): The name of the new entity.
        model_name (str): The
        """

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
        """
        Deconstructs the object into its constituent parts.
        
        This method extracts key attributes of the object and returns them in a structured format. The returned tuple contains the class name, an empty list, and a dictionary of keyword arguments.
        
        Args:
        None
        
        Returns:
        A tuple containing:
        - str: The class name of the object.
        - list: An empty list.
        - dict: A dictionary with the following keys and values:
        - 'model_name' (str
        """

        kwargs = {
            "model_name": self.model_name,
            "old_name": self.old_name,
            "new_name": self.new_name,
        }
        return (self.__class__.__name__, [], kwargs)

    def state_forwards(self, app_label, state):
        """
        Rename a field in a Django model.
        
        Args:
        app_label (str): The label of the Django application containing the model.
        state (ModelState): An instance of ModelState representing the current state of the model.
        
        This method renames a specific field in a Django model. It uses the `rename_field` method of the `state` object to perform the renaming operation. The renamed field is part of the specified model within the given application label.
        """

        state.rename_field(
            app_label, self.model_name_lower, self.old_name, self.new_name
        )

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """
        Alters an existing field in a Django model.
        
        Args:
        app_label (str): The label of the Django app containing the model.
        schema_editor: The schema editor object used to perform the alteration.
        from_state: The current state of the application's models.
        to_state: The target state of the application's models after the alteration.
        
        This method alters an existing field in a Django model by using the `schema_editor` to modify the field from one model to another.
        """

        to_model = to_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, to_model):
            from_model = from_state.apps.get_model(app_label, self.model_name)
            schema_editor.alter_field(
                from_model,
                from_model._meta.get_field(self.old_name),
                to_model._meta.get_field(self.new_name),
            )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        """
        Alters a field in a Django model during a database migration.
        
        Args:
        app_label (str): The label of the Django app containing the model.
        schema_editor: The schema editor object used to perform the alteration.
        from_state: The current state of the application's models.
        to_state: The target state of the application's models after the migration.
        
        This method alters a field in a Django model by renaming it from `new_name` to `old_name`. It checks
        """

        to_model = to_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, to_model):
            from_model = from_state.apps.get_model(app_label, self.model_name)
            schema_editor.alter_field(
                from_model,
                from_model._meta.get_field(self.new_name),
                to_model._meta.get_field(self.old_name),
            )

    def describe(self):
        """
        Generates a descriptive string for renaming a field.
        
        Args:
        self: The instance of the class containing the old name, model name, and new name.
        
        Returns:
        A string describing the action of renaming a field from `old_name` to `new_name` on the specified `model_name`.
        """

        return "Rename field %s on %s to %s" % (
            self.old_name,
            self.model_name,
            self.new_name,
        )

    @property
    def migration_name_fragment(self):
        """
        Generates a migration name fragment based on the old and new names of a model field, and the model's name.
        
        Args:
        self (Migration): The current migration object.
        
        Returns:
        str: A string representing the migration name fragment.
        
        Keyword Arguments:
        - `old_name_lower` (str): The lowercase version of the old name of the model field.
        - `model_name_lower` (str): The lowercase version of the model's name.
        - `new
        """

        return "rename_%s_%s_%s" % (
            self.old_name_lower,
            self.model_name_lower,
            self.new_name_lower,
        )

    def references_field(self, model_name, name, app_label):
        """
        Generates a reference field for a given model.
        
        Args:
        model_name (str): The name of the model.
        name (str): The name of the field.
        app_label (str): The label of the application.
        
        Returns:
        bool: True if the field is a reference field, False otherwise.
        
        This function checks if the given model has a reference field by comparing the provided field name with the old and new names of the reference field. It uses the `references
        """

        return self.references_model(model_name, app_label) and (
            name.lower() == self.old_name_lower or name.lower() == self.new_name_lower
        )

    def reduce(self, operation, app_label):
        """
        Reduces the given operation by checking if it is a `RenameField` operation that affects the same model and field names. If so, returns a new `RenameField` operation with updated names. Otherwise, skips `FieldOperation.reduce` and checks if the operation references the old or new field names.
        
        Args:
        operation (FieldOperation): The operation to be reduced.
        app_label (str): The application label of the model.
        
        Returns:
        list: A list containing a new
        """

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
