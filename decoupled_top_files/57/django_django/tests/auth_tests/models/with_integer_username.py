"""
```markdown
This Python file defines a custom Django user model and its associated manager. It overrides the default username field with an integer field and provides methods for creating and retrieving users based on their integer usernames.

#### Classes:
- **IntegerUsernameUserManager**: A custom user manager that extends `BaseUserManager` and provides methods for creating and retrieving users.
  - `create_user`: Creates a new user with a given integer username and password.
  - `get_by_natural_key`: Retrieves a user by their integer username.
  
- **IntegerUsernameUser**: A custom user model that extends `AbstractBaseUser` and uses the custom manager.
  - Fields: `username` (an integer field) and `password` (a string field
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class IntegerUsernameUserManager(BaseUserManager):
    def create_user(self, username, password):
        """
        Creates a new user with the given username and password.
        
        Args:
        username (str): The username of the new user.
        password (str): The password of the new user.
        
        Returns:
        User: The newly created user object.
        
        This function creates a new user instance using the provided username and sets the password using `set_password`. The user is then saved to the database using `save`.
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
