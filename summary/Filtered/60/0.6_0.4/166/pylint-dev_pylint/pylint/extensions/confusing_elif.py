# Licensed under the GPL: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# For details: https://github.com/PyCQA/pylint/blob/main/LICENSE
# Copyright (c) https://github.com/PyCQA/pylint/blob/main/CONTRIBUTORS.txt

from __future__ import annotations

from typing import TYPE_CHECKING

from astroid import nodes

from pylint.checkers import BaseChecker
from pylint.checkers.utils import only_required_for_messages

if TYPE_CHECKING:
    from pylint.lint import PyLinter


class ConfusingConsecutiveElifChecker(BaseChecker):
    """Checks if "elif" is used right after an indented block that finishes with "if" or
    "elif" itself.
    """

    name = "confusing_elif"
    msgs = {
        "R5601": (
            "Consecutive elif with differing indentation level, consider creating a function to separate the inner elif",
            "confusing-consecutive-elif",
            "Used when an elif statement follows right after an indented block which itself ends with if or elif. "
            "It may not be ovious if the elif statement was willingly or mistakenly unindented. "
            "Extracting the indented if statement into a separate function might avoid confusion and prevent errors.",
        )
    }

    @only_required_for_messages("confusing-consecutive-elif")
    def visit_if(self, node: nodes.If) -> None:
        """
        Visit an 'If' node in the AST.
        
        Args:
        node (nodes.If): The 'If' node to be visited.
        
        This function checks if the body of the 'If' node ends with another 'If' node
        that has no 'else' clause. If there is an 'elif' block and the body ends with
        another 'If' node, it adds a message indicating that the 'If' and 'elif' blocks
        are confusingly consecutive.
        
        Returns:
        None
        """

        body_ends_with_if = isinstance(
            node.body[-1], nodes.If
        ) and self._has_no_else_clause(node.body[-1])
        if node.has_elif_block() and body_ends_with_if:
            self.add_message("confusing-consecutive-elif", node=node.orelse[0])

    @staticmethod
    def _has_no_else_clause(node: nodes.If) -> bool:
        """
        Determine if an 'if' node has no 'else' clause or if the 'else' clause contains only 'if' nodes.
        
        Args:
        node (nodes.If): The 'if' node to check.
        
        Returns:
        bool: True if the 'if' node has no 'else' clause or if the 'else' clause contains only 'if' nodes, False otherwise.
        """

        orelse = node.orelse
        while orelse and isinstance(orelse[0], nodes.If):
            orelse = orelse[0].orelse
        if not orelse or isinstance(orelse[0], nodes.If):
            return True
        return False


def register(linter: PyLinter) -> None:
    linter.register_checker(ConfusingConsecutiveElifChecker(linter))
