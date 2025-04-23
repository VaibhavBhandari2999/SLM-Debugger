from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.db import models


class CustomEmailFieldUserManager(BaseUserManager):
    def create_user(self, username, password, email):
        """
        Create a new user instance.
        
        Args:
        username (str): The username for the new user.
        password (str): The password for the new user.
        email (str): The email address for the new user.
        
        Returns:
        User: The newly created user instance.
        
        This function creates a new user instance with the provided username, sets the password, assigns the email address, and saves the user to the database.
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
