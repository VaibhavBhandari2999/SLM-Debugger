from django.db.migrations.serializer import BaseSerializer


class RangeSerializer(BaseSerializer):
    def serialize(self):
        """
        Serializes a Python object into a string representation.
        
        This function takes a Python object and returns a string representation along with a list of import statements required to deserialize the object. The object's class module is identified and, if the class is a range (which is implemented in psycopg2._range but imported from psycopg2.extras), the module is adjusted accordingly.
        
        Parameters:
        self (object): The object to be serialized.
        
        Returns:
        tuple: A tuple containing the string representation of the object and
        """

        module = self.value.__class__.__module__
        # Ranges are implemented in psycopg2._range but the public import
        # location is psycopg2.extras.
        module = 'psycopg2.extras' if module == 'psycopg2._range' else module
        return '%s.%r' % (module, self.value), {'import %s' % module}
