from django.db.migrations.serializer import BaseSerializer


class RangeSerializer(BaseSerializer):
    def serialize(self):
        """
        Serializes a given value into a string representation.
        
        This function takes a value and returns a string representation of it, along with an import statement for the module containing the value's class. It is particularly useful for serializing objects that are part of the psycopg2 library, especially ranges.
        
        Parameters:
        self (object): The object to be serialized. Typically, this is an instance of a class that needs to be serialized for storage or transmission.
        
        Returns:
        tuple: A tuple containing the serialized string
        """

        module = self.value.__class__.__module__
        # Ranges are implemented in psycopg2._range but the public import
        # location is psycopg2.extras.
        module = "psycopg2.extras" if module == "psycopg2._range" else module
        return "%s.%r" % (module, self.value), {"import %s" % module}
