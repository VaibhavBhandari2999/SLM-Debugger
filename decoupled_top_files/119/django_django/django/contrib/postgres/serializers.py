from django.db.migrations.serializer import BaseSerializer


class RangeSerializer(BaseSerializer):
    def serialize(self):
        """
        Serializes an object into a string representation.
        
        Args:
        self: The instance of the class containing the value to be serialized.
        
        Returns:
        A tuple containing the serialized string and a dictionary with an import statement.
        
        Important Functions:
        - `self.value.__class__.__module__`: Retrieves the module name of the class of the value to be serialized.
        - `psycopg2.extras`: Used as the module name when serializing range objects.
        - `"%s.%
        """

        module = self.value.__class__.__module__
        # Ranges are implemented in psycopg2._range but the public import
        # location is psycopg2.extras.
        module = "psycopg2.extras" if module == "psycopg2._range" else module
        return "%s.%r" % (module, self.value), {"import %s" % module}
