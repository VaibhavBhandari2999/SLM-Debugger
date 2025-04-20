from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class IntegerUsernameUserManager(BaseUserManager):
    def create_user(self, username, password):
        """
        Creates a new user in the database.
        
        Parameters:
        username (str): The username for the new user.
        password (str): The password for the new user.
        
        Returns:
        user (User): The newly created user object.
        
        This function creates a new user with the specified username and password. The password is securely hashed before being stored. The user is then saved to the database using the current database connection.
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

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['username', 'password']

    objects = IntegerUsernameUserManager()
