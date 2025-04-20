from django.db.migrations.serializer import BaseSerializer


class RangeSerializer(BaseSerializer):
    def serialize(self):
        """
        Serializes a Python object into a string representation.
        
        This function takes a Python object and returns a string representation of it along with the necessary import statement for deserialization. The function handles special cases for ranges, which are imported from psycopg2.extras instead of psycopg2._range.
        
        Parameters:
        self (object): The object to be serialized.
        
        Returns:
        tuple: A tuple containing the serialized string and a dictionary with the import statement.
        
        Example:
        >>> obj = range(1, 5
        """

        module = self.value.__class__.__module__
        # Ranges are implemented in psycopg2._range but the public import
        # location is psycopg2.extras.
        module = 'psycopg2.extras' if module == 'psycopg2._range' else module
        return '%s.%r' % (module, self.value), {'import %s' % module}
