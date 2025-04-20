from django.db.migrations.serializer import BaseSerializer


class RangeSerializer(BaseSerializer):
    def serialize(self):
        """
        Serializes a value into a string representation.
        
        This function takes a value and serializes it into a string format that can be used for storage or transmission. The function identifies the class module of the value and, if the class is a range (specifically from psycopg2._range), it uses the public import location psycopg2.extras. It returns a tuple containing the serialized string and a dictionary with an import statement for the module.
        
        Parameters:
        self (object): The object to be serialized.
        """

        module = self.value.__class__.__module__
        # Ranges are implemented in psycopg2._range but the public import
        # location is psycopg2.extras.
        module = 'psycopg2.extras' if module == 'psycopg2._range' else module
        return '%s.%r' % (module, self.value), {'import %s' % module}
