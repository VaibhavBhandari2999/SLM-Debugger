from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.db import models


class CustomEmailFieldUserManager(BaseUserManager):
    def create_user(self, username, password, email):
        """
        Create a new user instance.
        
        This function creates a new user instance with the provided username, password, and email. The password is securely hashed before being stored.
        
        Parameters:
        username (str): The username for the new user.
        password (str): The password for the new user, which will be hashed.
        email (str): The email address for the new user.
        
        Returns:
        User: The newly created user instance.
        
        Note:
        The user instance is saved to the database using the
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
