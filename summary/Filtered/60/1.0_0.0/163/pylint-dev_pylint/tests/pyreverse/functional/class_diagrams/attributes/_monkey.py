# This is not a standalone test
# Monkey class is called from Tree class in delayed_external_monkey_patching.py


class Monkey:
    def __init__(self, name):
        """
        Initialize a new instance of the class.
        
        Args:
        name (str): The name of the instance.
        
        Attributes:
        name (str): The name of the instance.
        tree (Tree): An instance of the Tree class with monkey-patched attribute `has_tasty_bananas` set to True.
        """

        # pylint: disable=import-outside-toplevel
        from delayed_external_monkey_patching import Tree

        self.name = name
        self.tree = Tree()
        self.tree.has_tasty_bananas = True  # This monkey patching will increase the number of items in instance_attrs for `Tree`
