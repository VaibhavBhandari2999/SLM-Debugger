import pickle
from unittest import TestCase

from django.core.exceptions import ValidationError


class PickableValidationErrorTestCase(TestCase):
    def test_validationerror_is_picklable(self):
        """
        Test the picklability of ValidationError objects.
        
        This function checks if ValidationError objects and their error lists can be pickled and unpickled without losing their integrity. It tests various scenarios including single error messages, lists of error messages, nested ValidationError objects, and error messages with a dictionary format.
        
        Parameters:
        None
        
        Returns:
        None
        
        Assertions:
        - The unpickled ValidationError object is the same as the original.
        - The unpickled error message matches the original.
        - The
        """

        original = ValidationError("a", code="something")
        unpickled = pickle.loads(pickle.dumps(original))
        self.assertIs(unpickled, unpickled.error_list[0])
        self.assertEqual(original.message, unpickled.message)
        self.assertEqual(original.code, unpickled.code)

        original = ValidationError("a", code="something")
        unpickled = pickle.loads(pickle.dumps(ValidationError(original)))
        self.assertIs(unpickled, unpickled.error_list[0])
        self.assertEqual(original.message, unpickled.message)
        self.assertEqual(original.code, unpickled.code)

        original = ValidationError(["a", "b"])
        unpickled = pickle.loads(pickle.dumps(original))
        self.assertEqual(
            original.error_list[0].message, unpickled.error_list[0].message
        )
        self.assertEqual(
            original.error_list[1].message, unpickled.error_list[1].message
        )

        original = ValidationError(["a", "b"])
        unpickled = pickle.loads(pickle.dumps(ValidationError(original)))
        self.assertEqual(
            original.error_list[0].message, unpickled.error_list[0].message
        )
        self.assertEqual(
            original.error_list[1].message, unpickled.error_list[1].message
        )

        original = ValidationError([ValidationError("a"), ValidationError("b")])
        unpickled = pickle.loads(pickle.dumps(original))
        self.assertIs(unpickled.args[0][0], unpickled.error_list[0])
        self.assertEqual(
            original.error_list[0].message, unpickled.error_list[0].message
        )
        self.assertEqual(
            original.error_list[1].message, unpickled.error_list[1].message
        )

        message_dict = {"field1": ["a", "b"], "field2": ["c", "d"]}
        original = ValidationError(message_dict)
        unpickled = pickle.loads(pickle.dumps(original))
        self.assertEqual(unpickled.message_dict, message_dict)
