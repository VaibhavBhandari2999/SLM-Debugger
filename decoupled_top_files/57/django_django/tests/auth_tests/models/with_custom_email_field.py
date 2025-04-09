"""
```markdown
This Python file defines a custom user model for Django applications. It introduces a custom user manager `CustomEmailFieldUserManager` and a custom user model `CustomEmailField`. The custom user model extends `AbstractBaseUser` and overrides the default fields to use an email field instead of a username for authentication. The custom manager provides a method to create users with a specified username, password, and email.

Key Responsibilities:
- `CustomEmailFieldUserManager`: Manages the creation of users with a custom method `create_user`.
- `CustomEmailField`: Represents a custom user model with fields for username, password, and email. It also handles user authentication based on the email field.

Interactions:
- The `CustomEmailField
"""
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.db import models


class CustomEmailFieldUserManager(BaseUserManager):
    def create_user(self, username, password, email):
        """
        Creates a new user with the given username, password, and email.
        
        Args:
        username (str): The username of the user.
        password (str): The password of the user.
        email (str): The email address of the user.
        
        Returns:
        User: The newly created user object.
        
        This function sets the password using `set_password` method, saves the user using `save` method, and returns the user object.
        """

        user = self.model(username=username)
        user.set_password(password)
        user.email_address = email
        user.save(using=self._db)
        return user


class CustomEmailField(AbstractBaseUser):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    email_address = models.EmailField()
    is_active = models.BooleanField(default=True)

    EMAIL_FIELD = 'email_address'
    USERNAME_FIELD = 'username'

    objects = CustomEmailFieldUserManager()
