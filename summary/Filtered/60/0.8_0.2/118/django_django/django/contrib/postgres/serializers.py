from django.db.migrations.serializer import BaseSerializer


class RangeSerializer(BaseSerializer):
    def serialize(self):
        """
        Serializes a Python object into a string representation.
        
        This function takes a Python object and returns a string representation of it, along with a list of import statements required to deserialize the object. The function handles special cases for psycopg2 range objects, ensuring they are correctly serialized and deserialized.
        
        Parameters:
        self (object): The object to be serialized.
        
        Returns:
        tuple: A tuple containing the serialized string and a list of import statements.
        
        Example:
        >>> obj = psycopg2._range.Range(
        """

        module = self.value.__class__.__module__
        # Ranges are implemented in psycopg2._range but the public import
        # location is psycopg2.extras.
        module = "psycopg2.extras" if module == "psycopg2._range" else module
        return "%s.%r" % (module, self.value), {"import %s" % module}
