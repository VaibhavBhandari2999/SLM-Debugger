from django.core import checks
from django.db import models


class ModelRaisingMessages(models.Model):
    @classmethod
    def check(self, **kwargs):
        """
        Checks for various issues in the provided data.
        
        This method generates a list of warnings and errors based on the input parameters.
        
        Parameters:
        **kwargs: Arbitrary keyword arguments. These are used to provide context for the checks.
        
        Returns:
        list: A list of CheckMessage objects, where each object represents a warning or an error found during the check process.
        """

        return [
            checks.Warning('First warning', hint='Hint', obj='obj'),
            checks.Warning('Second warning', obj='a'),
            checks.Error('An error', hint='Error hint'),
        ]
