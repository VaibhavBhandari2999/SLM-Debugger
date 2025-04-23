from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.db import models


class CustomEmailFieldUserManager(BaseUserManager):
    def create_user(self, username, password, email):
        """
        Creates a new user instance with the provided username, password, and email.
        
        Args:
        username (str): The username for the new user.
        password (str): The password for the new user.
        email (str): The email address for the new user.
        
        Returns:
        user (model instance): The newly created user instance.
        
        Note:
        - The password is automatically hashed using `set_password`.
        - The user is saved using the database specified by `_db`.
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
