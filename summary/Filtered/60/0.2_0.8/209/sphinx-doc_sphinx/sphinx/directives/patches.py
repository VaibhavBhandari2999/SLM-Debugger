from __future__ import annotations

import os
from os import path
from typing import TYPE_CHECKING, Any, cast

from docutils import nodes
from docutils.nodes import Node, make_id
from docutils.parsers.rst import directives
from docutils.parsers.rst.directives import images, tables
from docutils.parsers.rst.directives.misc import Meta  # type: ignore[attr-defined]
from docutils.parsers.rst.roles import set_classes

from sphinx.directives import optional_int
from sphinx.domains.math import MathDomain
from sphinx.locale import __
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective
from sphinx.util.nodes import set_source_info
from sphinx.util.osutil import SEP, os_path, relpath
from sphinx.util.typing import OptionSpec

if TYPE_CHECKING:
    from sphinx.application import Sphinx


logger = logging.getLogger(__name__)


class Figure(images.Figure):
    """The figure directive which applies `:name:` option to the figure node
    instead of the image node.
    """

    def run(self) -> list[Node]:
        """
        Runs the parent class's run method and processes the resulting nodes.
        
        This function is designed to handle the output of a parent class's run method, which is expected to return a list of nodes. It performs several operations on the returned nodes, such as setting a name, copying the line number from the image node to the caption node, and ensuring the output is a single node. If the output is a system message or a list of two nodes, it returns the output as is.
        
        Parameters:
        """

        name = self.options.pop('name', None)
        result = super().run()
        if len(result) == 2 or isinstance(result[0], nodes.system_message):
            return result

        assert len(result) == 1
        figure_node = cast(nodes.figure, result[0])
        if name:
            # set ``name`` to figure_node if given
            self.options['name'] = name
            self.add_name(figure_node)

        # copy lineno from image node
        if figure_node.line is None and len(figure_node) == 2:
            caption = cast(nodes.caption, figure_node[1])
            figure_node.line = caption.line

        return [figure_node]


class CSVTable(tables.CSVTable):
    """The csv-table directive which searches a CSV file from Sphinx project's source
    directory when an absolute path is given via :file: option.
    """

    def run(self) -> list[Node]:
        if 'file' in self.options and self.options['file'].startswith((SEP, os.sep)):
            env = self.state.document.settings.env
            filename = self.options['file']
            if path.exists(filename):
                logger.warning(__('":file:" option for csv-table directive now recognizes '
                                  'an absolute path as a relative path from source directory. '
                                  'Please update your document.'),
                               location=(env.docname, self.lineno))
            else:
                abspath = path.join(env.srcdir, os_path(self.options['file'][1:]))
                docdir = path.dirname(env.doc2path(env.docname))
                self.options['file'] = relpath(abspath, docdir)

        return super().run()


class Code(SphinxDirective):
    """Parse and mark up content of a code block.

    This is compatible with docutils' :rst:dir:`code` directive.
    """
    optional_arguments = 1
    option_spec: OptionSpec = {
        'class': directives.class_option,
        'force': directives.flag,
        'name': directives.unchanged,
        'number-lines': optional_int,
    }
    has_content = True

    def run(self) -> list[Node]:
        self.assert_has_content()

        set_classes(self.options)
        code = '\n'.join(self.content)
        node = nodes.literal_block(code, code,
                                   classes=self.options.get('classes', []),
                                   force='force' in self.options,
                                   highlight_args={})
        self.add_name(node)
        set_source_info(self, node)

        if self.arguments:
            # highlight language specified
            node['language'] = self.arguments[0]
        else:
            # no highlight language specified.  Then this directive refers the current
            # highlight setting via ``highlight`` directive or ``highlight_language``
            # configuration.
            node['language'] = self.env.temp_data.get('highlight_language',
                                                      self.config.highlight_language)

        if 'number-lines' in self.options:
            node['linenos'] = True

            # if number given, treat as lineno-start.
            if self.options['number-lines']:
                node['highlight_args']['linenostart'] = self.options['number-lines']

        return [node]


class MathDirective(SphinxDirective):
    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec: OptionSpec = {
        'label': directives.unchanged,
        'name': directives.unchanged,
        'class': directives.class_option,
        'nowrap': directives.flag,
    }

    def run(self) -> list[Node]:
        latex = '\n'.join(self.content)
        if self.arguments and self.arguments[0]:
            latex = self.arguments[0] + '\n\n' + latex
        label = self.options.get('label', self.options.get('name'))
        node = nodes.math_block(latex, latex,
                                classes=self.options.get('class', []),
                                docname=self.env.docname,
                                number=None,
                                label=label,
                                nowrap='nowrap' in self.options)
        self.add_name(node)
        self.set_source_info(node)

        ret: list[Node] = [node]
        self.add_target(ret)
        return ret

    def add_target(self, ret: list[Node]) -> None:
        """
        Adds a target node to the math block in the document.
        
        This function processes a math block node and adds a target node to it if the math block has a label. If the math block is part of a document where the 'math_number_all' configuration is enabled, the function automatically assigns a label to the math block. The function then registers the label to the math domain and adds a target node to the math block.
        
        Parameters:
        ret (list[Node]): A list containing the math block
        """

        node = cast(nodes.math_block, ret[0])

        # assign label automatically if math_number_all enabled
        if node['label'] == '' or (self.config.math_number_all and not node['label']):
            seq = self.env.new_serialno('sphinx.ext.math#equations')
            node['label'] = "%s:%d" % (self.env.docname, seq)

        # no targets and numbers are needed
        if not node['label']:
            return

        # register label to domain
        domain = cast(MathDomain, self.env.get_domain('math'))
        domain.note_equation(self.env.docname, node['label'], location=node)
        node['number'] = domain.get_equation_number_for(node['label'])

        # add target node
        node_id = make_id('equation-%s' % node['label'])
        target = nodes.target('', '', ids=[node_id])
        self.state.document.note_explicit_target(target)
        ret.insert(0, target)


def setup(app: Sphinx) -> dict[str, Any]:
    """
    Setup function for Sphinx documentation.
    
    This function registers various directives with the Sphinx application for custom
    document processing. It is typically used in the `conf.py` file of a Sphinx project.
    
    Parameters:
    app (Sphinx): The Sphinx application object.
    
    Returns:
    dict: A dictionary containing metadata about the extension, including its version.
    """

    directives.register_directive('figure', Figure)
    directives.register_directive('meta', Meta)
    directives.register_directive('csv-table', CSVTable)
    directives.register_directive('code', Code)
    directives.register_directive('math', MathDirective)

    return {
        'version': 'builtin',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
