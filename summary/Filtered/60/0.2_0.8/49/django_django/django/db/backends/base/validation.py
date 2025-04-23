class BaseDatabaseValidation:
    """Encapsulate backend-specific validation."""
    def __init__(self, connection):
        self.connection = connection

    def check(self, **kwargs):
        return []

    def check_field(self, field, **kwargs):
        """
        Checks a given field for validation errors.
        
        Args:
        field (Field): The field to be checked.
        **kwargs: Additional keyword arguments that may be required by the backend.
        
        Returns:
        list: A list of error messages if any validation errors are found, otherwise an empty list.
        
        This function performs validation checks on a given field. It first checks if the backend has a `check_field_type` method. If so, it then checks if the field is a related field (i.e.,
        """

        errors = []
        # Backends may implement a check_field_type() method.
        if (hasattr(self, 'check_field_type') and
                # Ignore any related fields.
                not getattr(field, 'remote_field', None)):
            # Ignore fields with unsupported features.
            db_supports_all_required_features = all(
                getattr(self.connection.features, feature, False)
                for feature in field.model._meta.required_db_features
            )
            if db_supports_all_required_features:
                field_type = field.db_type(self.connection)
                # Ignore non-concrete fields.
                if field_type is not None:
                    errors.extend(self.check_field_type(field, field_type))
        return errors
