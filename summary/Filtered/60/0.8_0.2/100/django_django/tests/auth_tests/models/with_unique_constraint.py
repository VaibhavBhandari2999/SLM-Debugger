from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class CustomUserWithUniqueConstraintManager(BaseUserManager):
    def create_superuser(self, username, password):
        """
        Creates a new superuser with the specified username and password.
        
        Parameters:
        username (str): The username for the superuser.
        password (str): The password for the superuser.
        
        Returns:
        User: The newly created superuser object.
        
        This function is used to create a superuser in the system. It takes a username and password, creates a new user object, sets the password, and saves the user to the database.
        """

        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomUserWithUniqueConstraint(AbstractBaseUser):
    username = models.CharField(max_length=150)

    objects = CustomUserWithUniqueConstraintManager()
    USERNAME_FIELD = "username"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["username"], name="unique_custom_username"),
        ]
