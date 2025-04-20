from django.http import HttpRequest
from django.test import SimpleTestCase, ignore_warnings
from django.utils.deprecation import RemovedInDjango40Warning


@ignore_warnings(category=RemovedInDjango40Warning)
class TestDeprecatedIsAjax(SimpleTestCase):
    def test_is_ajax(self):
        """
        Tests the is_ajax() method of HttpRequest.
        
        This function checks the behavior of the is_ajax() method in HttpRequest objects.
        It first creates an HttpRequest object without any AJAX headers and verifies that is_ajax() returns False.
        Then, it sets the 'HTTP_X_REQUESTED_WITH' header to 'XMLHttpRequest' and confirms that is_ajax() returns True.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Assertions:
        - is_ajax() returns False for a standard HttpRequest object.
        - is_ajax
        """

        request = HttpRequest()
        self.assertIs(request.is_ajax(), False)
        request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        self.assertIs(request.is_ajax(), True)
