from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Group
from django.db import models


class Email(models.Model):
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)


class CustomUserWithFKManager(BaseUserManager):
    def create_superuser(self, username, email, group, password):
        """
        Creates a superuser with the specified details.
        
        Args:
        username (str): The username of the superuser.
        email (str): The email address of the superuser.
        group (int): The group ID associated with the superuser.
        password (str): The password for the superuser.
        
        Returns:
        User: The created superuser object.
        
        Note:
        This function is used to create a superuser with the given parameters. The user's password is set using `set_password
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
