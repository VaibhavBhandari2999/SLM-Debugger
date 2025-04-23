# Levels
DEBUG = 10
INFO = 20
WARNING = 30
ERROR = 40
CRITICAL = 50


class CheckMessage:

    def __init__(self, level, msg, hint=None, obj=None, id=None):
        """
        Initialize a custom log message.
        
        Args:
        level (int): The severity level of the log message.
        msg (str): The message content to be logged.
        hint (str, optional): Additional hint or information for the message. Defaults to None.
        obj (any, optional): An object associated with the log message. Defaults to None.
        id (str, optional): A unique identifier for the log message. Defaults to None.
        
        This function initializes a log message with the specified level
        """

        assert isinstance(level, int), "The first argument should be level."
        self.level = level
        self.msg = msg
        self.hint = hint
        self.obj = obj
        self.id = id

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            all(getattr(self, attr) == getattr(other, attr)
                for attr in ['level', 'msg', 'hint', 'obj', 'id'])
        )

    def __str__(self):
        """
        This function returns a string representation of a validation error or warning in a Django application.
        
        Parameters:
        - self: The instance of the class containing the error details.
        - obj: The object being validated, which can be a model instance or a model class.
        - id (optional): The ID of the validation error.
        - hint (optional): Additional hint or advice related to the validation error.
        
        Returns:
        A string that describes the validation error or warning, including the object being validated, the error ID (
        """

        from django.db import models

        if self.obj is None:
            obj = "?"
        elif isinstance(self.obj, models.base.ModelBase):
            # We need to hardcode ModelBase and Field cases because its __str__
            # method doesn't return "applabel.modellabel" and cannot be changed.
            obj = self.obj._meta.label
        else:
            obj = str(self.obj)
        id = "(%s) " % self.id if self.id else ""
        hint = "\n\tHINT: %s" % self.hint if self.hint else ''
        return "%s: %s%s%s" % (obj, id, self.msg, hint)

    def __repr__(self):
        return "<%s: level=%r, msg=%r, hint=%r, obj=%r, id=%r>" % \
            (self.__class__.__name__, self.level, self.msg, self.hint, self.obj, self.id)

    def is_serious(self, level=ERROR):
        return self.level >= level

    def is_silenced(self):
        from django.conf import settings
        return self.id in settings.SILENCED_SYSTEM_CHECKS


class Debug(CheckMessage):
    def __init__(self, *args, **kwargs):
        super().__init__(DEBUG, *args, **kwargs)


class Info(CheckMessage):
    def __init__(self, *args, **kwargs):
        super().__init__(INFO, *args, **kwargs)


class Warning(CheckMessage):
    def __init__(self, *args, **kwargs):
        super().__init__(WARNING, *args, **kwargs)


class Error(CheckMessage):
    def __init__(self, *args, **kwargs):
        super().__init__(ERROR, *args, **kwargs)


class Critical(CheckMessage):
    def __init__(self, *args, **kwargs):
        super().__init__(CRITICAL, *args, **kwargs)
