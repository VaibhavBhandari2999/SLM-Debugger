"""
```markdown
# Summary

This Python script is part of a Django project and is designed to test the rendering of multiline strings using Django's template engine. It includes a single test case that verifies whether a multiline string is rendered correctly without any modifications.

## Classes

- `MultilineTests`: A subclass of `SimpleTestCase` from Django's testing framework. This class contains a single test method to check the rendering of a multiline string.

## Functions

- `test_multiline01`: A test method within the `MultilineTests` class. It sets up a template with a given multiline string and checks if the rendered output matches the input string.

## Key Responsibilities

- Ensuring that multiline strings are rendered accurately by Django's template engine
"""
from django.test import SimpleTestCase

from ..utils import setup

multiline_string = """
Hello,
boys.
How
are
you
gentlemen.
"""


class MultilineTests(SimpleTestCase):

    @setup({'multiline01': multiline_string})
    def test_multiline01(self):
        output = self.engine.render_to_string('multiline01')
        self.assertEqual(output, multiline_string)
