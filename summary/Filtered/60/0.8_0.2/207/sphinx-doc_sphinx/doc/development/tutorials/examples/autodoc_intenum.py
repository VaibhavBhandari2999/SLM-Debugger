from enum import IntEnum
from typing import Any, Optional

from docutils.statemachine import StringList

from sphinx.application import Sphinx
from sphinx.ext.autodoc import ClassDocumenter, bool_option


class IntEnumDocumenter(ClassDocumenter):
    objtype = 'intenum'
    directivetype = ClassDocumenter.objtype
    priority = 10 + ClassDocumenter.priority
    option_spec = dict(ClassDocumenter.option_spec)
    option_spec['hex'] = bool_option

    @classmethod
    def can_document_member(cls,
                            member: Any, membername: str,
                            isattr: bool, parent: Any) -> bool:
        try:
            return issubclass(member, IntEnum)
        except TypeError:
            return False

    def add_directive_header(self, sig: str) -> None:
        super().add_directive_header(sig)
        self.add_line('   :final:', self.get_sourcename())

    def add_content(self,
        """
        Add additional content to the enum documentation.
        
        Args:
        more_content (Optional[StringList]): Additional content to be added to the enum documentation.
        no_docstring (bool, optional): If set to True, no docstring will be added. Defaults to False.
        
        This method appends additional content to the enum documentation. It first calls the superclass's `add_content` method with the provided `more_content` and `no_docstring` parameters. Then, it retrieves the source name and the enum
        """

                    more_content: Optional[StringList],
                    no_docstring: bool = False
                    ) -> None:

        super().add_content(more_content, no_docstring)

        source_name = self.get_sourcename()
        enum_object: IntEnum = self.object
        use_hex = self.options.hex
        self.add_line('', source_name)

        for the_member_name, enum_member in enum_object.__members__.items():
            the_member_value = enum_member.value
            if use_hex:
                the_member_value = hex(the_member_value)

            self.add_line(
                f"**{the_member_name}**: {the_member_value}", source_name)
            self.add_line('', source_name)


def setup(app: Sphinx) -> None:
    app.setup_extension('sphinx.ext.autodoc')  # Require autodoc extension
    app.add_autodocumenter(IntEnumDocumenter)
