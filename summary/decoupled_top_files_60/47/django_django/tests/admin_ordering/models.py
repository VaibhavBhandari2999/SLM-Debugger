from django.contrib import admin
from django.db import models


class Band(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField()
    rank = models.IntegerField()

    class Meta:
        ordering = ('name',)


class Song(models.Model):
    band = models.ForeignKey(Band, models.CASCADE)
    name = models.CharField(max_length=100)
    duration = models.IntegerField()
    other_interpreters = models.ManyToManyField(Band, related_name='covers')

    class Meta:
        ordering = ('name',)


class SongInlineDefaultOrdering(admin.StackedInline):
    model = Song


class SongInlineNewOrdering(admin.StackedInline):
    model = Song
    ordering = ('duration',)


class DynOrderingBandAdmin(admin.ModelAdmin):

    def get_ordering(self, request):
        """
        Function to determine the ordering of a list based on the user's permissions.
        
        Parameters:
        - request (HttpRequest): The HTTP request object containing user information.
        
        Returns:
        - list: A list of strings representing the field names to order by.
        
        Description:
        This function returns a list of field names to order a list of objects. If the user is a superuser, the list is ordered by 'rank'. Otherwise, the list is ordered by 'name'.
        """

        if request.user.is_superuser:
            return ['rank']
        else:
            return ['name']
