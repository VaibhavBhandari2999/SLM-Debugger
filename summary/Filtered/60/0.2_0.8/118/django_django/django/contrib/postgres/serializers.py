from django.db.migrations.serializer import BaseSerializer


class RangeSerializer(BaseSerializer):
    def serialize(self):
        """
        Serializes a given value into a string representation suitable for database storage.
        
        This function takes a value and returns a string representation of it along with import statements required to deserialize it. It handles special cases for ranges, which are imported from psycopg2.extras instead of psycopg2._range.
        
        Parameters:
        self (object): The object containing the value to be serialized.
        
        Returns:
        tuple: A tuple containing the serialized string and a dictionary of import statements. The serialized string is in the format "{module
        """

        module = self.value.__class__.__module__
        # Ranges are implemented in psycopg2._range but the public import
        # location is psycopg2.extras.
        module = "psycopg2.extras" if module == "psycopg2._range" else module
        return "%s.%r" % (module, self.value), {"import %s" % module}
