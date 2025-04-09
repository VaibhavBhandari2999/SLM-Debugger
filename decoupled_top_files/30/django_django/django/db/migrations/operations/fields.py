from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields import NOT_PROVIDED
from django.utils.functional import cached_property

from .base import Operation
from .utils import (
    ModelTuple, field_references_model, is_referenced_by_foreign_key,
)


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
        return self.is_same_model_operation(operation) and self.name_lower == operation.name_lower

    def references_model(self, name, app_label=None):
        """
        Determines whether a given model references the current model.
        
        Args:
        name (str): The name of the model to check.
        app_label (str, optional): The application label of the model. Defaults to None.
        
        Returns:
        bool: True if the given model references the current model, False otherwise.
        
        Important Functions:
        - `field_references_model`: Checks if a specific field references the current model.
        - `name_lower`: Converts the provided model name to lowercase for
        """

        name_lower = name.lower()
        if name_lower == self.model_name_lower:
            return True
        if self.field:
            return field_references_model(self.field, ModelTuple(app_label, name_lower))
        return False

    def references_field(self, model_name, name, app_label=None):
        """
        Determines whether the given model field references the current field.
        
        Args:
        model_name (str): The name of the model being checked.
        name (str): The name of the field being checked.
        app_label (str, optional): The application label of the model. Defaults to None.
        
        Returns:
        bool: True if the given model field references the current field, otherwise False.
        
        Important Functions:
        - `model_name_lower`: Converts the model name to lowercase for comparison
        """

        model_name_lower = model_name.lower()
        # Check if this operation locally references the field.
        if model_name_lower == self.model_name_lower:
            if name == self.name:
                return True
            elif self.field and hasattr(self.field, 'from_fields') and name in self.field.from_fields:
                return True
        # Check if this operation remotely references the field.
        if self.field:
            model_tuple = ModelTuple(app_label, model_name_lower)
            remote_field = self.field.remote_field
            if remote_field:
                if (ModelTuple.from_model(remote_field.model) == model_tuple and
                        (not hasattr(self.field, 'to_fields') or
                            name in self.field.to_fields or None in self.field.to_fields)):
                    return True
                through = getattr(remote_field, 'through', None)
                if (through and ModelTuple.from_model(through) == model_tuple and
                        (getattr(remote_field, 'through_fields', None) is None or
                            name in remote_field.through_fields)):
                    return True
        return False

    def reduce(self, operation, app_label=None):
        """
        Reduces the given operation based on whether it references the field.
        
        Args:
        operation (Operation): The operation to be reduced.
        app_label (str, optional): The application label to filter operations by. Defaults to None.
        
        Returns:
        bool: True if the operation does not reference the field, False otherwise.
        """

        return (
            super().reduce(operation, app_label=app_label) or
            not operation.references_field(self.model_name, self.name, app_label)
        )


class AddField(FieldOperation):
    """Add a field to a model."""

    def __init__(self, model_name, name, field, preserve_default=True):
        self.preserve_default = preserve_default
        super().__init__(model_name, name, field)

    def deconstruct(self):
        """
        Deconstructs the current object into a tuple containing the class name, an empty list of positional arguments, and a dictionary of keyword arguments.
        
        Args:
        None
        
        Returns:
        A tuple with three elements:
        - The class name (`str`) of the current object.
        - An empty list (`list`) of positional arguments.
        - A dictionary (`dict`) of keyword arguments, which includes:
        - `model_name` (`str`): The name of the model.
        """

        kwargs = {
            'model_name': self.model_name,
            'name': self.name,
            'field': self.field,
        }
        if self.preserve_default is not True:
            kwargs['preserve_default'] = self.preserve_default
        return (
            self.__class__.__name__,
            [],
            kwargs
        )

    def state_forwards(self, app_label, state):
        """
        Updates the state with a new field for the given model. If `preserve_default` is False, sets the field's default value to NOT_PROVIDED. Otherwise, retains the original field. The function appends the field to the model's fields list and reloads the model if it's not a relational field.
        
        Args:
        app_label (str): The application label of the model.
        state (ModelState): The current state of the model.
        
        Returns:
        None: This function modifies
        """

        # If preserve default is off, don't use the default for future state
        if not self.preserve_default:
            field = self.field.clone()
            field.default = NOT_PROVIDED
        else:
            field = self.field
        state.models[app_label, self.model_name_lower].fields.append((self.name, field))
        # Delay rendering of relationships if it's not a relational field
        delay = not field.is_relation
        state.reload_model(app_label, self.model_name_lower, delay=delay)

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
        from_state: The current state of the application before the migration.
        to_state: The target state of the application after the migration.
        
        Returns:
        None
        
        Effects:
        - Removes a field from the specified model in the given app label
        """

        from_model = from_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, from_model):
            schema_editor.remove_field(from_model, from_model._meta.get_field(self.name))

    def describe(self):
        return "Add field %s to %s" % (self.name, self.model_name)

    def reduce(self, operation, app_label=None):
        """
        Reduces a given operation to a set of operations that can be applied to the model.
        
        Args:
        operation (FieldOperation): The operation to reduce.
        app_label (str, optional): The application label for the model. Defaults to None.
        
        Returns:
        list: A list of operations that can be applied to the model.
        
        Summary:
        This method processes a given `FieldOperation` and returns a list of operations based on the type of the operation. It handles `Alter
        """

        if isinstance(operation, FieldOperation) and self.is_same_field_operation(operation):
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
        return super().reduce(operation, app_label=app_label)


class RemoveField(FieldOperation):
    """Remove a field from a model."""

    def deconstruct(self):
        """
        Deconstructs the object into its class name, parameters, and keyword arguments.
        
        Args:
        None
        
        Returns:
        tuple: A tuple containing the class name, an empty list of positional arguments, and a dictionary of keyword arguments.
        
        Keyword Arguments:
        model_name (str): The name of the model.
        name (str): The name of the object.
        """

        kwargs = {
            'model_name': self.model_name,
            'name': self.name,
        }
        return (
            self.__class__.__name__,
            [],
            kwargs
        )

    def state_forwards(self, app_label, state):
        """
        Modifies the fields of a model in the given state. It removes the specified field from the model's fields list and reloads the model if it is not a relational field.
        
        Args:
        app_label (str): The application label of the Django app containing the model.
        state (ModelState): The current state of the models.
        
        Returns:
        None: This function modifies the state in place and does not return anything.
        
        Keyword Arguments:
        delay (bool): Whether to delay rendering
        """

        new_fields = []
        old_field = None
        for name, instance in state.models[app_label, self.model_name_lower].fields:
            if name != self.name:
                new_fields.append((name, instance))
            else:
                old_field = instance
        state.models[app_label, self.model_name_lower].fields = new_fields
        # Delay rendering of relationships if it's not a relational field
        delay = not old_field.is_relation
        state.reload_model(app_label, self.model_name_lower, delay=delay)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """
        Removes a field from a model in the specified application label.
        
        Args:
        app_label (str): The name of the Django app containing the model.
        schema_editor: An instance of the schema editor used to perform database operations.
        from_state: The current state of the application's models.
        to_state: The target state of the application's models.
        
        Returns:
        None
        
        Effects:
        - Removes a field from the specified model.
        - Utilizes `allow
        """

        from_model = from_state.apps.get_model(app_label, self.model_name)
        if self.allow_migrate_model(schema_editor.connection.alias, from_model):
            schema_editor.remove_field(from_model, from_model._meta.get_field(self.name))

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

    def reduce(self, operation, app_label=None):
        """
        Reduces the given operation based on the provided criteria.
        
        Args:
        operation (object): The operation to be reduced.
        app_label (str, optional): The application label to filter by. Defaults to None.
        
        Returns:
        list: A list containing the reduced operation(s), or an empty list if no reduction is applicable.
        
        Notes:
        - This method checks if the operation is an instance of `DeleteModel` and matches the model name.
        - If the operation matches,
        """

        from .models import DeleteModel
        if isinstance(operation, DeleteModel) and operation.name_lower == self.model_name_lower:
            return [operation]
        return super().reduce(operation, app_label=app_label)


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
        Deconstructs the current object into a tuple containing the class name, an empty list of positional arguments, and a dictionary of keyword arguments.
        
        Args:
        None
        
        Returns:
        A tuple with three elements:
        - The class name (`str`) of the current object.
        - An empty list (`list`) of positional arguments.
        - A dictionary (`dict`) of keyword arguments, which includes:
        - `model_name` (`str`): The name of the model.
        """

        kwargs = {
            'model_name': self.model_name,
            'name': self.name,
            'field': self.field,
        }
        if self.preserve_default is not True:
            kwargs['preserve_default'] = self.preserve_default
        return (
            self.__class__.__name__,
            [],
            kwargs
        )

    def state_forwards(self, app_label, state):
        """
        Modifies the model fields in the given state for the specified app label. If `preserve_default` is False, the default value of the field is reset to NOT_PROVIDED. The function then updates the fields dictionary of the model with the modified field. If the field is not a relational field and is not referenced by a foreign key, the function delays rendering of relationships. Finally, it reloads the model with the updated fields.
        
        Args:
        app_label (str): The application label of
        """

        if not self.preserve_default:
            field = self.field.clone()
            field.default = NOT_PROVIDED
        else:
            field = self.field
        state.models[app_label, self.model_name_lower].fields = [
            (n, field if n == self.name else f)
            for n, f in
            state.models[app_label, self.model_name_lower].fields
        ]
        # TODO: investigate if old relational fields must be reloaded or if it's
        # sufficient if the new field is (#27737).
        # Delay rendering of relationships if it's not a relational field and
        # not referenced by a foreign key.
        delay = (
            not field.is_relation and
            not is_referenced_by_foreign_key(state, self.model_name_lower, self.field, self.name)
        )
        state.reload_model(app_label, self.model_name_lower, delay=delay)

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

    def reduce(self, operation, app_label=None):
        """
        Reduces a given operation by either returning the operation itself or a list of operations that include both the original operation and an `AlterField` operation.
        
        Args:
        operation (Operation): The operation to be reduced.
        app_label (str, optional): The application label for the model. Defaults to None.
        
        Returns:
        list[Operation] | Operation: A list containing the original operation and an `AlterField` operation if applicable, or the original operation itself.
        
        Notes:
        """

        if isinstance(operation, RemoveField) and self.is_same_field_operation(operation):
            return [operation]
        elif isinstance(operation, RenameField) and self.is_same_field_operation(operation):
            return [
                operation,
                AlterField(
                    model_name=self.model_name,
                    name=operation.new_name,
                    field=self.field,
                ),
            ]
        return super().reduce(operation, app_label=app_label)


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
        
        Args:
        None
        
        Returns:
        A tuple containing:
        - The class name of the object being deconstructed (str)
        - An empty list ([])
        - A dictionary with the following keys and values:
        - 'model_name' (str): The name of the model.
        - 'old_name' (str): The old name of the entity being renamed.
        - 'new_name' (str): The new
        """

        kwargs = {
            'model_name': self.model_name,
            'old_name': self.old_name,
            'new_name': self.new_name,
        }
        return (
            self.__class__.__name__,
            [],
            kwargs
        )

    def state_forwards(self, app_label, state):
        """
        Renames a field in a Django model state.
        
        Args:
        app_label (str): The application label of the model.
        state (ModelState): The current state of the model.
        
        Returns:
        None: This function modifies the `state` object in place.
        
        Important Functions:
        - `fields`: Accesses the fields of the model.
        - `from_fields`: Modifies the related fields that reference the renamed field.
        - `is_referenced_by_foreign_key`: Checks
        """

        model_state = state.models[app_label, self.model_name_lower]
        # Rename the field
        fields = model_state.fields
        found = False
        delay = True
        for index, (name, field) in enumerate(fields):
            if not found and name == self.old_name:
                fields[index] = (self.new_name, field)
                found = True
            # Fix from_fields to refer to the new field.
            from_fields = getattr(field, 'from_fields', None)
            if from_fields:
                field.from_fields = tuple([
                    self.new_name if from_field_name == self.old_name else from_field_name
                    for from_field_name in from_fields
                ])
            # Delay rendering of relationships if it's not a relational
            # field and not referenced by a foreign key.
            delay = delay and (
                not field.is_relation and
                not is_referenced_by_foreign_key(state, self.model_name_lower, field, self.name)
            )
        if not found:
            raise FieldDoesNotExist(
                "%s.%s has no field named '%s'" % (app_label, self.model_name, self.old_name)
            )
        # Fix index/unique_together to refer to the new field
        options = model_state.options
        for option in ('index_together', 'unique_together'):
            if option in options:
                options[option] = [
                    [self.new_name if n == self.old_name else n for n in together]
                    for together in options[option]
                ]
        # Fix to_fields to refer to the new field.
        model_tuple = app_label, self.model_name_lower
        for (model_app_label, model_name), model_state in state.models.items():
            for index, (name, field) in enumerate(model_state.fields):
                remote_field = field.remote_field
                if remote_field:
                    remote_model_tuple = self._get_model_tuple(
                        remote_field.model, model_app_label, model_name
                    )
                    if remote_model_tuple == model_tuple:
                        if getattr(remote_field, 'field_name', None) == self.old_name:
                            remote_field.field_name = self.new_name
                        to_fields = getattr(field, 'to_fields', None)
                        if to_fields:
                            field.to_fields = tuple([
                                self.new_name if to_field_name == self.old_name else to_field_name
                                for to_field_name in to_fields
                            ])
        state.reload_model(app_label, self.model_name_lower, delay=delay)

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
        return "Rename field %s on %s to %s" % (self.old_name, self.model_name, self.new_name)

    def references_field(self, model_name, name, app_label=None):
        """
        Generates a reference field for a given model.
        
        Args:
        model_name (str): The name of the model.
        name (str): The name of the field.
        app_label (str, optional): The application label for the model. Defaults to None.
        
        Returns:
        bool: True if the field is a reference field, False otherwise.
        """

        return self.references_model(model_name) and (
            name.lower() == self.old_name_lower or
            name.lower() == self.new_name_lower
        )

    def reduce(self, operation, app_label=None):
        """
        Reduces the given operation if applicable.
        
        Args:
        operation: The operation to be reduced.
        app_label: The application label (optional).
        
        Returns:
        A list of operations if the given operation can be reduced, otherwise returns the original operation or an empty list.
        
        Summary:
        This method checks if the given operation is a `RenameField` and if it applies to the same model and field name. If so, it returns a new `RenameField` operation with the old
        """

        if (isinstance(operation, RenameField) and
                self.is_same_model_operation(operation) and
                self.new_name_lower == operation.old_name_lower):
            return [
                RenameField(
                    self.model_name,
                    self.old_name,
                    operation.new_name,
                ),
            ]
        # Skip `FieldOperation.reduce` as we want to run `references_field`
        # against self.new_name.
        return (
            super(FieldOperation, self).reduce(operation, app_label=app_label) or
            not operation.references_field(self.model_name, self.new_name, app_label)
        )
