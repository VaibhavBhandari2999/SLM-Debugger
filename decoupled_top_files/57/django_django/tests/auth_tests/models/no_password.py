"""
The provided Python file contains Django-specific code for managing and creating custom user models. It defines two main components:

1. **UserManager**: A custom manager class for creating users. It includes methods for creating regular users and superusers. The `_create_user` method handles the creation of a new user instance, while `create_superuser` provides a way to create a superuser.

2. **NoPasswordUser**: A custom user model that inherits from `AbstractBaseUser`. This model overrides the default `password` field and `last_login` field, making them `None`. It also sets the `username` as the unique identifier for the user and uses the `UserManager` for user management.

This file is crucial for setting up a custom
"""
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def _create_user(self, username, **extra_fields):
        """
        Creates a new user with the given username and additional fields.
        
        Args:
        username (str): The username of the user to be created.
        extra_fields (dict): Additional fields to be set on the user object.
        
        Returns:
        User: The newly created user object.
        
        Important Functions:
        - model: The user model class used to create the user instance.
        - save: Saves the user instance to the database using the specified database connection.
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
