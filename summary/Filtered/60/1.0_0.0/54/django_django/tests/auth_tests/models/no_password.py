from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def _create_user(self, username, **extra_fields):
        """
        Create a new user.
        
        This method creates a new user with the provided username and any additional fields specified in extra_fields. The user is saved to the database using the current database connection.
        
        Parameters:
        username (str): The username for the new user.
        extra_fields (dict): Additional fields to set on the user, such as email, password, etc.
        
        Returns:
        User: The newly created user object.
        
        Note:
        The user is saved using the current database connection specified by self._
        """

        user = self.model(username=username, **extra_fields)
        user.save(using=self._db)
        return user

    def create_superuser(self, username=None, **extra_fields):
        return self._create_user(username, **extra_fields)


class NoPasswordUser(AbstractBaseUser):
    password = None
    last_login = None
    username = models.CharField(max_length=50, unique=True)

    USERNAME_FIELD = 'username'
    objects = UserManager()
