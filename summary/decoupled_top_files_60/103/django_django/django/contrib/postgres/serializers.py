from django.db.migrations.serializer import BaseSerializer


class RangeSerializer(BaseSerializer):
    def serialize(self):
        """
        Serializes a Python object into a string representation suitable for storage.
        
        This function takes a Python object and returns a string representation that can be used for serialization. It identifies the module of the object's class and handles a special case for psycopg2's range objects, which are imported from psycopg2.extras. The function returns a tuple containing the serialized string and a dictionary with an import statement.
        
        Parameters:
        self (object): The object to be serialized.
        
        Returns:
        tuple: A tuple containing:
        """

        module = self.value.__class__.__module__
        # Ranges are implemented in psycopg2._range but the public import
        # location is psycopg2.extras.
        module = "psycopg2.extras" if module == "psycopg2._range" else module
        return "%s.%r" % (module, self.value), {"import %s" % module}
