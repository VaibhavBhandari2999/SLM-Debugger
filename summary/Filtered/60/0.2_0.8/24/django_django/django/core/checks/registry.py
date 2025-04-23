from itertools import chain

from django.utils.itercompat import is_iterable


class Tags:
    """
    Built-in tags for internal checks.
    """
    admin = 'admin'
    caches = 'caches'
    compatibility = 'compatibility'
    database = 'database'
    models = 'models'
    security = 'security'
    signals = 'signals'
    templates = 'templates'
    translation = 'translation'
    urls = 'urls'


class CheckRegistry:

    def __init__(self):
        self.registered_checks = set()
        self.deployment_checks = set()

    def register(self, check=None, *tags, **kwargs):
        """
        Can be used as a function or a decorator. Register given function
        `f` labeled with given `tags`. The function should receive **kwargs
        and return list of Errors and Warnings.

        Example::

            registry = CheckRegistry()
            @registry.register('mytag', 'anothertag')
            def my_check(apps, **kwargs):
                # ... perform checks and collect `errors` ...
                return errors
            # or
            registry.register(my_check, 'mytag', 'anothertag')
        """
        def inner(check):
            """
            Add a check to the deployment or registered checks based on the 'deploy' keyword argument.
            
            This function is a decorator that modifies the provided check function by setting its 'tags' attribute to the specified 'tags'. It then adds the check to the appropriate set of checks (deployment checks if 'deploy' is True, otherwise registered checks) and returns the modified check function.
            
            Parameters:
            check (function): The check function to be modified and added.
            
            Keyword Arguments:
            deploy (bool, optional):
            """

            check.tags = tags
            checks = self.deployment_checks if kwargs.get('deploy') else self.registered_checks
            checks.add(check)
            return check

        if callable(check):
            return inner(check)
        else:
            if check:
                tags += (check,)
            return inner

    def run_checks(self, app_configs=None, tags=None, include_deployment_checks=False):
        """
        Run all registered checks and return list of Errors and Warnings.
        """
        errors = []
        checks = self.get_checks(include_deployment_checks)

        if tags is not None:
            checks = [check for check in checks if not set(check.tags).isdisjoint(tags)]
        else:
            # By default, 'database'-tagged checks are not run as they do more
            # than mere static code analysis.
            checks = [check for check in checks if Tags.database not in check.tags]

        for check in checks:
            new_errors = check(app_configs=app_configs)
            assert is_iterable(new_errors), (
                "The function %r did not return a list. All functions registered "
                "with the checks registry must return a list." % check)
            errors.extend(new_errors)
        return errors

    def tag_exists(self, tag, include_deployment_checks=False):
        return tag in self.tags_available(include_deployment_checks)

    def tags_available(self, deployment_checks=False):
        """
        Retrieve the set of available tags for checks associated with the deployment.
        
        Args:
        deployment_checks (bool, optional): If True, includes checks related to deployment. Defaults to False.
        
        Returns:
        set: A set of tags from all checks.
        """

        return set(chain.from_iterable(
            check.tags for check in self.get_checks(deployment_checks)
        ))

    def get_checks(self, include_deployment_checks=False):
        checks = list(self.registered_checks)
        if include_deployment_checks:
            checks.extend(self.deployment_checks)
        return checks


registry = CheckRegistry()
register = registry.register
run_checks = registry.run_checks
tag_exists = registry.tag_exists
