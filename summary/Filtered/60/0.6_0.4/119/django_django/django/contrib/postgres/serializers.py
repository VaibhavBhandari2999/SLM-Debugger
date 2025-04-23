from django.db.migrations.serializer import BaseSerializer


class RangeSerializer(BaseSerializer):
    def serialize(self):
        """
        Serializes a given value into a string representation suitable for database storage.
        
        This function takes a value and returns a string representation that can be used
        to store the value in a database. It handles special cases for ranges, which are
        implemented in psycopg2._range but imported as psycopg2.extras.
        
        Parameters:
        self (object): The object containing the value to be serialized.
        
        Returns:
        tuple: A tuple containing the serialized string and a dictionary with an import statement.
        
        Example:
        >>>
        """

        module = self.value.__class__.__module__
        # Ranges are implemented in psycopg2._range but the public import
        # location is psycopg2.extras.
        module = "psycopg2.extras" if module == "psycopg2._range" else module
        return "%s.%r" % (module, self.value), {"import %s" % module}
