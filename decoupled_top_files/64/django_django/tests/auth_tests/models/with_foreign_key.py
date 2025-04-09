"""
```markdown
This Django application defines a custom user model and a manager for creating users. 

**Classes:**
- `Email`: A model representing an email address.
- `CustomUserWithFKManager`: A custom user manager that extends `BaseUserManager` to handle superuser creation.
- `CustomUserWithFK`: A custom user model that extends `AbstractBaseUser` and uses the custom manager.

**Functions:**
- `CustomUserWithFKManager.create_superuser`: Creates a superuser with specified username, email, group, and password.

**Key Responsibilities:**
- Manages user creation and authentication.
- Associates users with email addresses and groups.

**Interactions:**
- `CustomUserWithFK` uses `CustomUser
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Group
from django.db import models


class Email(models.Model):
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)


class CustomUserWithFKManager(BaseUserManager):
    def create_superuser(self, username, email, group, password):
        """
        Creates a superuser with the given username, email, group, and password.
        
        Args:
        username (str): The username of the superuser.
        email (str): The email address of the superuser.
        group (int): The ID of the group associated with the superuser.
        password (str): The password for the superuser.
        
        Returns:
        User: The created superuser object.
        
        This function creates a new superuser by setting the provided username, email,
        """

        user = self.model(username_id=username, email_id=email, group_id=group)
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomUserWithFK(AbstractBaseUser):
    username = models.ForeignKey(Email, models.CASCADE, related_name='primary')
    email = models.ForeignKey(Email, models.CASCADE, to_field='email', related_name='secondary')
    group = models.ForeignKey(Group, models.CASCADE)

    custom_objects = CustomUserWithFKManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'group']
