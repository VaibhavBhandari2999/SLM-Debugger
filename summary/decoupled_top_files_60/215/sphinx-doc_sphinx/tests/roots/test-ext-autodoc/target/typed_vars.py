#: attr1
attr1: str = ''
#: attr2
attr2: str
#: attr3
attr3 = ''  # type: str


class _Descriptor:
    def __init__(self, name):
        self.__doc__ = "This is {}".format(name)
    def __get__(self):
        pass


class Class:
    attr1: int = 0
    attr2: int
    attr3 = 0  # type: int

    descr4: int = _Descriptor("descr4")

    def __init__(self):
        """
        Initialize the object with default values for its attributes.
        
        Attributes:
        attr4 (int): The fourth attribute of the object, initialized to 0.
        attr5 (int): The fifth attribute of the object, uninitialized.
        attr6 (int): The sixth attribute of the object, initialized to 0.
        """

        self.attr4: int = 0     #: attr4
        self.attr5: int         #: attr5
        self.attr6 = 0          # type: int
        """attr6"""


class Derived(Class):
    attr7: int
