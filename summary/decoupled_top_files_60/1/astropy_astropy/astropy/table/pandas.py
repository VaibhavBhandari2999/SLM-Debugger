ascii_coded = (
    "Ò♙♙♙♙♙♙♙♙♌♐♐♌♙♙♙♙♙♙♌♌♙♙Ò♙♙♙♙♙♙♙♘♐♐♐♈♙♙♙♙♙♌♐♐♐♔Ò♙♙♌♈♙♙♌♐♈♈♙♙♙♙♙♙♙♙♈♐♐♙Ò♙♐♙♙♙♐♐♙♙♙"
    "♙♙♙♙♙♙♙♙♙♙♙♙Ò♐♔♙♙♘♐♐♙♙♌♐♐♔♙♙♌♌♌♙♙♙♌Ò♐♐♙♙♘♐♐♌♙♈♐♈♙♙♙♈♐♐♙♙♘♔Ò♐♐♌♙♘♐♐♐♌♌♙♙♌♌♌♙♈♈♙♌♐"
    "♐Ò♘♐♐♐♌♐♐♐♐♐♐♌♙♈♙♌♐♐♐♐♐♔Ò♘♐♐♐♐♐♐♐♐♐♐♐♐♈♈♐♐♐♐♐♐♙Ò♙♘♐♐♐♐♈♐♐♐♐♐♐♙♙♐♐♐♐♐♙♙Ò♙♙♙♈♈♈♙♙♐"
    "♐♐♐♐♔♙♐♐♐♐♈♙♙Ò♙♙♙♙♙♙♙♙♙♈♈♐♐♐♙♈♈♈♙♙♙♙Ò"
)
ascii_uncoded = "".join([chr(ord(c) - 200) for c in ascii_coded])
url = "https://media.giphy.com/media/e24Q8FKE2mxRS/giphy.gif"
message_coded = "ĘĩĶĬĩĻ÷ĜĩĪĴĭèıĶļĭĺĩīļıķĶ"
message_uncoded = "".join([chr(ord(c) - 200) for c in message_coded])

try:
    from IPython import display

    html = display.Image(url=url)._repr_html_()

    class HTMLWithBackup(display.HTML):
        def __init__(self, data, backup_text):
            super().__init__(data)
            self.backup_text = backup_text

        def __repr__(self):
            """
            Generate a string representation of the object.
            
            This method returns a string that represents the object. If the object has a 'backup_text' attribute and it is not None, it returns the value of 'backup_text'. Otherwise, it calls the __repr__ method of the superclass.
            
            :returns: A string representation of the object.
            :rtype: str
            """

            if self.backup_text is None:
                return super().__repr__()
            else:
                return self.backup_text

    dhtml = HTMLWithBackup(html, ascii_uncoded)
    display.display(dhtml)
except ImportError:
    print(ascii_uncoded)
except (UnicodeEncodeError, SyntaxError):
    pass
