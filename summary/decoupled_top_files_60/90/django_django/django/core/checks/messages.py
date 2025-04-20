# Levels
DEBUG = 10
INFO = 20
WARNING = 30
ERROR = 40
CRITICAL = 50


class CheckMessage:

    def __init__(self, level, msg, hint=None, obj=None, id=None):
        """
        Initialize a LogEntry object.
        
        Args:
        level (int): The logging level of the message.
        msg (str): The message to be logged.
        hint (str, optional): Additional hint or information about the message. Defaults to None.
        obj (object, optional): The object associated with the message. Defaults to None.
        id (str, optional): An identifier for the message. Defaults to None.
        
        Raises:
        TypeError: If the level is not an integer.
        
        Returns:
        """

        if not isinstance(level, int):
            raise TypeError('The first argument should be level.')
        self.level = level
        self.msg = msg
        self.hint = hint
        self.obj = obj
        self.id = id

    def __eq__(self, other):
        """
        Method to check if two instances of a class are equal.
        
        Parameters:
        - other (object): The object to compare against.
        
        Returns:
        - bool: True if the two instances are of the same class and have the same 'level', 'msg', 'hint', 'obj', and 'id' attributes, False otherwise.
        
        This method is used to compare two instances of a class to determine if they are equal based on their attributes.
        """

        return (
            isinstance(other, self.__class__) and
            all(getattr(self, attr) == getattr(other, attr)
                for attr in ['level', 'msg', 'hint', 'obj', 'id'])
        )

    def __str__(self):
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
(CheckMessage):
    def __init__(self, *args, **kwargs):
        super().__init__(CRITICAL, *args, **kwargs)
