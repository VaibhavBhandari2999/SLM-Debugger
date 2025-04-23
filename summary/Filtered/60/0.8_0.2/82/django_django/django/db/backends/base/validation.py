class BaseDatabaseValidation:
    """Encapsulate backend-specific validation."""
    def __init__(self, connection):
        self.connection = connection

    def check(self, **kwargs):
        return []

    def check_field(self, field, **kwargs):
        """
        Checks a field for validation errors.
        
        Args:
        field (Field): The field to check.
        **kwargs: Additional keyword arguments that may be used by the backend.
        
        Returns:
        list: A list of error messages if any errors are found, otherwise an empty list.
        
        This function checks a given field for validation errors. It first checks if the backend has a `check_field_type` method and if the field is not a related field. If the database supports all required features for the field,
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
