from django.db.migrations.serializer import BaseSerializer


class RangeSerializer(BaseSerializer):
    def serialize(self):
        """
        Serializes a Python object into a string representation.
        
        This function takes a value object and returns a string representation of its class module and value. If the value is a range object, it is treated as a psycopg2._range object and its module is replaced with 'psycopg2.extras'. The function also returns a dictionary with an import statement for the module.
        
        Parameters:
        self (object): The object to be serialized.
        
        Returns:
        tuple: A tuple containing the string representation of the class
        """

        module = self.value.__class__.__module__
        # Ranges are implemented in psycopg2._range but the public import
        # location is psycopg2.extras.
        module = "psycopg2.extras" if module == "psycopg2._range" else module
        return "%s.%r" % (module, self.value), {"import %s" % module}
