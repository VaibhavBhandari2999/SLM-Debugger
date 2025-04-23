from docutils import nodes
from docutils.parsers.rst import Directive


class HelloWorld(Directive):

    def run(self):
        paragraph_node = nodes.paragraph(text='Hello World!')
        return [paragraph_node]


def setup(app):
    """
    Setup function for the Sphinx extension.
    
    This function is used to configure the Sphinx extension. It adds a new directive to the Sphinx application.
    
    Parameters:
    app (sphinx.application.Sphinx): The Sphinx application object.
    
    Returns:
    dict: A dictionary containing the version of the extension and information about its safety for parallel processing.
    """

    app.add_directive("helloworld", HelloWorld)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
