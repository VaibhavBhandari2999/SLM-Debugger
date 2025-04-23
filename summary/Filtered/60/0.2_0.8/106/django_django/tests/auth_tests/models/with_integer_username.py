from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class IntegerUsernameUserManager(BaseUserManager):
    def create_user(self, username, password):
        """
        Creates a new user instance with the given username and password.
        
        Args:
        username (str): The username for the new user.
        password (str): The password for the new user.
        
        Returns:
        User: The newly created user instance.
        
        Note:
        The password is securely hashed before being stored.
        The user is saved using the current database connection.
        """

        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def get_by_natural_key(self, username):
        return self.get(username=username)


class IntegerUsernameUser(AbstractBaseUser):
    username = models.IntegerField()
    password = models.CharField(max_length=255)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["username", "password"]

    objects = IntegerUsernameUserManager()
