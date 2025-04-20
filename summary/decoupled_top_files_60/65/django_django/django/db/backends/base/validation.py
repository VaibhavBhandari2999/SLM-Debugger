class BaseDatabaseValidation:
    """Encapsulate backend-specific validation."""
    def __init__(self, connection):
        self.connection = connection

    def check(self, **kwargs):
        return []

    def check_field(self, field, **kwargs):
        """
        Check a field for validation errors.
        
        This method checks a given field for any validation errors. It first checks if the instance has a `check_field_type` method. If so, and if the field is not a related field, it proceeds to check if the database supports all required features for the field. If the database supports all required features, it retrieves the database type of the field and checks the field type using the `check_field_type` method. The method returns a list of errors found during
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
