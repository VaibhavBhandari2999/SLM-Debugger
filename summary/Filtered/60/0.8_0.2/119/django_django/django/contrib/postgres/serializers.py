from django.db.migrations.serializer import BaseSerializer


class RangeSerializer(BaseSerializer):
    def serialize(self):
        """
        Serializes a Python object into a string representation suitable for storage in a database.
        
        This function takes a Python object and returns a string that represents the object's class and value, along with any necessary import statements. It is particularly useful for serializing objects that are not natively supported by the database, such as ranges.
        
        Parameters:
        self (object): The object to be serialized.
        
        Returns:
        tuple: A tuple containing the serialized string and a dictionary of import statements.
        
        Key Points:
        - The
        """

        module = self.value.__class__.__module__
        # Ranges are implemented in psycopg2._range but the public import
        # location is psycopg2.extras.
        module = "psycopg2.extras" if module == "psycopg2._range" else module
        return "%s.%r" % (module, self.value), {"import %s" % module}
