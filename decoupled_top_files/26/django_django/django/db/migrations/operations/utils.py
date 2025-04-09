from collections import namedtuple

from django.db.models.fields.related import RECURSIVE_RELATIONSHIP_CONSTANT


def is_referenced_by_foreign_key(state, model_name_lower, field, field_name):
    """
    Determines if a given field is referenced by a foreign key in another model.
    
    Args:
    state: The current state of the database models.
    model_name_lower: The lowercase name of the model being checked.
    field: The field object to check for foreign key references.
    field_name: The name of the field to check.
    
    Returns:
    bool: True if the field is referenced by a foreign key, False otherwise.
    
    This function iterates through all models in the given
    """

    for state_app_label, state_model in state.models:
        for _, f in state.models[state_app_label, state_model].fields:
            if (f.related_model and
                    '%s.%s' % (state_app_label, model_name_lower) == f.related_model.lower() and
                    hasattr(f, 'to_fields')):
                if (f.to_fields[0] is None and field.primary_key) or field_name in f.to_fields:
                    return True
    return False


class ModelTuple(namedtuple('ModelTupleBase', ('app_label', 'model_name'))):
    @classmethod
    def from_model(cls, model, app_label=None, model_name=None):
        """
        Take a model class or an 'app_label.ModelName' string and return a
        ModelTuple('app_label', 'modelname'). The optional app_label and
        model_name arguments are the defaults if "self" or "ModelName" are
        passed.
        """
        if isinstance(model, str):
            if model == RECURSIVE_RELATIONSHIP_CONSTANT:
                return cls(app_label, model_name)
            if '.' in model:
                return cls(*model.lower().split('.', 1))
            return cls(app_label, model.lower())
        return cls(model._meta.app_label, model._meta.model_name)

    def __eq__(self, other):
        """
        Checks if the current instance is equal to another object.
        
        Args:
        other (ModelTuple): The object to compare with.
        
        Returns:
        bool: True if the current instance is equal to `other`, False otherwise.
        
        Notes:
        - Compares the `model_name` attribute of both instances.
        - Considers the instances equal if either one of them has a missing `app_label`.
        - Inherits equality comparison behavior from the superclass using `super().__eq__(other)`.
        """

        if isinstance(other, ModelTuple):
            # Consider ModelTuple equal if their model_name is equal and either
            # one of them is missing an app_label.
            return self.model_name == other.model_name and (
                self.app_label is None or other.app_label is None or self.app_label == other.app_label
            )
        return super().__eq__(other)


def field_references_model(field, model_tuple):
    """Return whether or not field references model_tuple."""
    remote_field = field.remote_field
    if remote_field:
        if ModelTuple.from_model(remote_field.model) == model_tuple:
            return True
        through = getattr(remote_field, 'through', None)
        if through and ModelTuple.from_model(through) == model_tuple:
            return True
    return False
