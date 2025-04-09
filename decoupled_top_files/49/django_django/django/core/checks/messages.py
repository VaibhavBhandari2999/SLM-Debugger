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
        msg (str): The message to log.
        hint (str, optional): Additional hint or information about the message. Defaults to None.
        obj (object, optional): An object associated with the message. Defaults to None.
        id (str, optional): A unique identifier for the message. Defaults to None.
        
        Raises:
        AssertionError: If the `level` argument
        """

        assert isinstance(level, int), "The first argument should be level."
        self.level = level
        self.msg = msg
        self.hint = hint
        self.obj = obj
        self.id = id

    def __eq__(self, other):
        """
        Check if two instances of the class are equal.
        
        This method compares two instances of the same class by checking if their attributes 'level', 'msg', 'hint', 'obj', and 'id' are equal. It returns True if all these attributes match, otherwise False.
        
        Args:
        other (object): The object to compare with.
        
        Returns:
        bool: True if the instances are equal based on their attributes, False otherwise.
        """

        return (
            isinstance(other, self.__class__) and
            all(getattr(self, attr) == getattr(other, attr)
                for attr in ['level', 'msg', 'hint', 'obj', 'id'])
        )

    def __str__(self):
        """
        Generate a string representation of the object with the given message, ID, and hint.
        
        Args:
        self (object): The instance of the class containing the object, message, ID, and hint.
        
        Returns:
        str: A formatted string representation of the object with the given message, ID, and hint.
        
        Important Functions:
        - `self.obj`: The object being represented.
        - `self.id`: The ID of the object.
        - `self.hint`: Additional hint
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
