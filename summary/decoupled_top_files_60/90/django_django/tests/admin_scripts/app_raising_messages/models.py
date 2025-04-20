from django.core import checks
from django.db import models


class ModelRaisingMessages(models.Model):
    @classmethod
    def check(self, **kwargs):
        """
        check(self, **kwargs)
        
        Generate a list of warnings and errors based on the provided keyword arguments.
        
        Parameters:
        **kwargs: Arbitrary keyword arguments that are used to determine the checks to be performed.
        
        Returns:
        list: A list of checks.Warning and checks.Error objects indicating the issues found.
        """

        return [
            checks.Warning('First warning', hint='Hint', obj='obj'),
            checks.Warning('Second warning', obj='a'),
            checks.Error('An error', hint='Error hint'),
        ]
