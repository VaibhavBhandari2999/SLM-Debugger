# PermWrapper and PermLookupDict proxy the permissions system into objects that
# the template system can understand.


class PermLookupDict:
    def __init__(self, user, app_label):
        self.user, self.app_label = user, app_label

    def __repr__(self):
        return str(self.user.get_all_permissions())

    def __getitem__(self, perm_name):
        return self.user.has_perm("%s.%s" % (self.app_label, perm_name))

    def __iter__(self):
        """
        Summary:
        This function raises a TypeError indicating that the PermLookupDict object is not iterable.
        
        Parameters:
        None
        
        Returns:
        None
        
        Raises:
        TypeError: Raised when the object is attempted to be iterated over.
        
        Details:
        The PermLookupDict class is designed to prevent iteration, which is necessary to avoid conflicts with the __getitem__ method. This function is called when an attempt is made to iterate over an instance of PermLookupDict, and it raises a TypeError to indicate that this operation is not
        """

        # To fix 'item in perms.someapp' and __getitem__ interaction we need to
        # define __iter__. See #18979 for details.
        raise TypeError("PermLookupDict is not iterable.")

    def __bool__(self):
        return self.user.has_module_perms(self.app_label)


class PermWrapper:
    def __init__(self, user):
        self.user = user

    def __getitem__(self, app_label):
        return PermLookupDict(self.user, app_label)

    def __iter__(self):
        # I am large, I contain multitudes.
        raise TypeError("PermWrapper is not iterable.")

    def __contains__(self, perm_name):
        """
        Lookup by "someapp" or "someapp.someperm" in perms.
        """
        if '.' not in perm_name:
            # The name refers to module.
            return bool(self[perm_name])
        app_label, perm_name = perm_name.split('.', 1)
        return self[app_label][perm_name]


def auth(request):
    """
    Return context variables required by apps that use Django's authentication
    system.

    If there is no 'user' attribute in the request, use AnonymousUser (from
    django.contrib.auth).
    """
    if hasattr(request, 'user'):
        user = request.user
    else:
        from django.contrib.auth.models import AnonymousUser
        user = AnonymousUser()

    return {
        'user': user,
        'perms': PermWrapper(user),
    }
