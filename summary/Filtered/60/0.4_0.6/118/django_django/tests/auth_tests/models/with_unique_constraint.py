from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class CustomUserWithUniqueConstraintManager(BaseUserManager):
    def create_superuser(self, username, password):
        """
        Creates a superuser with the specified username and password.
        
        Args:
        username (str): The username for the superuser.
        password (str): The password for the superuser.
        
        Returns:
        User: The created superuser object.
        
        Note:
        This function sets the password using `set_password` and saves the user to the database using `save`.
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
