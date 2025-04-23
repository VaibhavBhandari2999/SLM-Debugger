from django.db.migrations.serializer import BaseSerializer


class RangeSerializer(BaseSerializer):
    def serialize(self):
        """
        Serializes a value to a string representation.
        
        This function takes a value and returns a string representation of it, along with import statements necessary for deserialization. It handles special cases for ranges, which are imported from `psycopg2.extras` instead of `psycopg2._range`.
        
        Parameters:
        self (object): The object to be serialized. This object should have a `value` attribute containing the value to be serialized.
        
        Returns:
        tuple: A tuple containing the serialized string and a
        """

        module = self.value.__class__.__module__
        # Ranges are implemented in psycopg2._range but the public import
        # location is psycopg2.extras.
        module = "psycopg2.extras" if module == "psycopg2._range" else module
        return "%s.%r" % (module, self.value), {"import %s" % module}
