from docutils import nodes
from docutils.parsers.rst import Directive


class HelloWorld(Directive):

    def run(self):
        paragraph_node = nodes.paragraph(text='Hello World!')
        return [paragraph_node]


def setup(app):
    """
    Setup function for the Sphinx extension.
    
    This function is called by Sphinx to initialize the extension. It registers a custom directive named "helloworld" with the Sphinx application.
    
    Parameters:
    app (sphinx.application.Sphinx): The Sphinx application object.
    
    Returns:
    dict: A dictionary containing extension metadata, including the version number and safety information for parallel processing.
    """

    app.add_directive("helloworld", HelloWorld)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
