import pickle

from django.db import DJANGO_VERSION_PICKLE_KEY, models
from django.test import SimpleTestCase
from django.utils.version import get_version


class ModelPickleTests(SimpleTestCase):
    def test_missing_django_version_unpickling(self):
        """
        #21430 -- Verifies a warning is raised for models that are
        unpickled without a Django version
        """
        class MissingDjangoVersion(models.Model):
            title = models.CharField(max_length=10)

            def __reduce__(self):
                """
                This function customizes the reduction process for an object. It returns a tuple that can be used to reconstruct the object. The function first calls the __reduce__ method of the superclass to get the initial reduction data. It then modifies the data by removing the item at the index specified by DJANGO_VERSION_PICKLE_KEY. The function returns the modified tuple.
                
                Parameters:
                - No explicit parameters are passed to this function; it relies on the internal state of the object.
                
                Returns:
                - A tuple that represents
                """

                reduce_list = super().__reduce__()
                data = reduce_list[-1]
                del data[DJANGO_VERSION_PICKLE_KEY]
                return reduce_list

        p = MissingDjangoVersion(title="FooBar")
        msg = "Pickled model instance's Django version is not specified."
        with self.assertRaisesMessage(RuntimeWarning, msg):
            pickle.loads(pickle.dumps(p))

    def test_unsupported_unpickle(self):
        """
        #21430 -- Verifies a warning is raised for models that are
        unpickled with a different Django version than the current
        """
        class DifferentDjangoVersion(models.Model):
            title = models.CharField(max_length=10)

            def __reduce__(self):
                """
                Reduces the object to a serializable format for pickling.
                
                This method is used to prepare the object for serialization, particularly when pickling. It extends the functionality of the base class's `__reduce__` method by modifying the serialized data. Specifically, it appends a version key to the serialized data, indicating compatibility with Django version 1.0.
                
                Returns:
                tuple: A tuple containing the reduced representation of the object, which includes the original base class's reduced representation and the modified
                """

                reduce_list = super().__reduce__()
                data = reduce_list[-1]
                data[DJANGO_VERSION_PICKLE_KEY] = '1.0'
                return reduce_list

        p = DifferentDjangoVersion(title="FooBar")
        msg = "Pickled model instance's Django version 1.0 does not match the current version %s." % get_version()
        with self.assertRaisesMessage(RuntimeWarning, msg):
            pickle.loads(pickle.dumps(p))

    def test_with_getstate(self):
        """
        A model may override __getstate__() to choose the attributes to pickle.
        """
        class PickledModel(models.Model):
            def __getstate__(self):
                state = super().__getstate__().copy()
                del state['dont_pickle']
                return state

        m = PickledModel()
        m.dont_pickle = 1
        dumped = pickle.dumps(m)
        self.assertEqual(m.dont_pickle, 1)
        reloaded = pickle.loads(dumped)
        self.assertFalse(hasattr(reloaded, 'dont_pickle'))
