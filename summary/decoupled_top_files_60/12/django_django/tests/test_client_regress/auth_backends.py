from django.contrib.auth.backends import ModelBackend

from .models import CustomUser


class CustomUserBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None):
        """
        Authenticate a user.
        
        This method checks if a user with the given username exists and if the provided password is correct.
        
        Parameters:
        request (HttpRequest): The HTTP request object (not used in this method).
        username (str): The username of the user to authenticate.
        password (str): The password to check against the user's password.
        
        Returns:
        CustomUser: The authenticated user object if the credentials are correct, otherwise None.
        """

        try:
            user = CustomUser.custom_objects.get_by_natural_key(username)
            if user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return CustomUser.custom_objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
