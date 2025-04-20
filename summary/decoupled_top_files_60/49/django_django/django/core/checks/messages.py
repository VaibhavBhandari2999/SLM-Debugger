# Levels
DEBUG = 10
INFO = 20
WARNING = 30
ERROR = 40
CRITICAL = 50


class CheckMessage:

    def __init__(self, level, msg, hint=None, obj=None, id=None):
        """
        Initialize a new instance of the class.
        
        Args:
        level (int): The logging level of the message.
        msg (str): The message to be logged.
        hint (str, optional): Additional hint or information about the message. Defaults to None.
        obj (object, optional): An object associated with the message. Defaults to None.
        id (str, optional): An identifier for the message. Defaults to None.
        
        Raises:
        AssertionError: If the level is not an integer.
        """

        assert isinstance(level, int), "The first argument should be level."
        self.level = level
        self.msg = msg
        self.hint = hint
        self.obj = obj
        self.id = id

    def __eq__(self, other):
        """
        Function: __eq__
        
        This method checks if the current instance is equal to another instance of the same class.
        
        Parameters:
        - other: The instance to compare with the current instance.
        
        Returns:
        - A boolean value indicating whether the current instance is equal to the other instance.
        
        Key Attributes Compared:
        - level: The severity level of the log message.
        - msg: The message content.
        - hint: Any additional hint or information.
        - obj: The object associated with the log message.
        - id:
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
