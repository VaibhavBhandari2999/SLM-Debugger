class FileProxyMixin:
    """
    A mixin class used to forward file methods to an underlaying file
    object.  The internal file object has to be called "file"::

        class FileProxy(FileProxyMixin):
            def __init__(self, file):
                self.file = file
    """

    encoding = property(lambda self: self.file.encoding)
    fileno = property(lambda self: self.file.fileno)
    flush = property(lambda self: self.file.flush)
    isatty = property(lambda self: self.file.isatty)
    newlines = property(lambda self: self.file.newlines)
    read = property(lambda self: self.file.read)
    readinto = property(lambda self: self.file.readinto)
    readline = property(lambda self: self.file.readline)
    readlines = property(lambda self: self.file.readlines)
    seek = property(lambda self: self.file.seek)
    tell = property(lambda self: self.file.tell)
    truncate = property(lambda self: self.file.truncate)
    write = property(lambda self: self.file.write)
    writelines = property(lambda self: self.file.writelines)

    @property
    def closed(self):
        return not self.file or self.file.closed

    def readable(self):
        if self.closed:
            return False
        if hasattr(self.file, 'readable'):
            return self.file.readable()
        return True

    def writable(self):
        """
        Determines if the file is writable.
        
        This method checks if the file is writable. It returns False if the file is closed. If the file object has a writable method, it uses that. Otherwise, it checks the mode of the file object to see if it includes 'w'.
        
        Parameters:
        self (File): The file object to check.
        
        Returns:
        bool: True if the file is writable, False otherwise.
        """

        if self.closed:
            return False
        if hasattr(self.file, 'writable'):
            return self.file.writable()
        return 'w' in getattr(self.file, 'mode', '')

    def seekable(self):
        if self.closed:
            return False
        if hasattr(self.file, 'seekable'):
            return self.file.seekable()
        return True

    def __iter__(self):
        return iter(self.file)
