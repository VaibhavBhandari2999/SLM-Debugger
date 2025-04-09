# Licensed under a 3-clause BSD style license - see LICENSE.rst
import operator

__all__ = ["BST"]


class MaxValue:
    """
    Represents an infinite value for purposes
    of tuple comparison.
    """

    def __gt__(self, other):
        return True

    def __ge__(self, other):
        return True

    def __lt__(self, other):
        return False

    def __le__(self, other):
        return False

    def __repr__(self):
        return "MAX"

    __str__ = __repr__


class MinValue:
    """
    The opposite of MaxValue, i.e. a representation of
    negative infinity.
    """

    def __lt__(self, other):
        return True

    def __le__(self, other):
        return True

    def __gt__(self, other):
        return False

    def __ge__(self, other):
        return False

    def __repr__(self):
        return "MIN"

    __str__ = __repr__


class Epsilon:
    """
    Represents the "next largest" version of a given value,
    so that for all valid comparisons we have
    x < y < Epsilon(y) < z whenever x < y < z and x, z are
    not Epsilon objects.

    Parameters
    ----------
    val : object
        Original value
    """

    __slots__ = ("val",)

    def __init__(self, val):
        self.val = val

    def __lt__(self, other):
        """
        __lt__(self, other) -> bool
        Compares the value of the current object with another object (other).
        Returns True if the value of the current object is less than the value of other, otherwise returns False.
        If the values are equal, returns False.
        
        Parameters:
        self: The current object being compared.
        other: The object to compare against.
        
        Returns:
        bool: True if self.val is less than other, False otherwise.
        """

        if self.val == other:
            return False
        return self.val < other

    def __gt__(self, other):
        """
        Compares the value of the current object with another object.
        
        Args:
        other: The object to compare against.
        
        Returns:
        bool: True if the value of the current object is greater than or equal to the value of the other object, False otherwise.
        
        Notes:
        - If the values are equal, returns True.
        - Otherwise, compares the values using the '>' operator.
        """

        if self.val == other:
            return True
        return self.val > other

    def __eq__(self, other):
        return False

    def __repr__(self):
        return repr(self.val) + " + epsilon"


class Node:
    """
    An element in a binary search tree, containing
    a key, data, and references to children nodes and
    a parent node.

    Parameters
    ----------
    key : tuple
        Node key
    data : list or int
        Node data
    """

    __lt__ = lambda x, y: x.key < y.key
    __le__ = lambda x, y: x.key <= y.key
    __eq__ = lambda x, y: x.key == y.key
    __ge__ = lambda x, y: x.key >= y.key
    __gt__ = lambda x, y: x.key > y.key
    __ne__ = lambda x, y: x.key != y.key
    __slots__ = ("key", "data", "left", "right")

    # each node has a key and data list
    def __init__(self, key, data):
        """
        Initialize a Node object.
        
        Args:
        key (int): The key value of the node.
        data (list or any): The data associated with the node. If not a list, it will be converted into a list.
        
        Attributes:
        key (int): The key value of the node.
        data (list): The data associated with the node, always stored as a list.
        left (Node): A reference to the left child node.
        right (Node): A reference
        """

        self.key = key
        self.data = data if isinstance(data, list) else [data]
        self.left = None
        self.right = None

    def replace(self, child, new_child):
        """
        Replace this node's child with a new child.
        """
        if self.left is not None and self.left == child:
            self.left = new_child
        elif self.right is not None and self.right == child:
            self.right = new_child
        else:
            raise ValueError("Cannot call replace() on non-child")

    def remove(self, child):
        """
        Remove the given child.
        """
        self.replace(child, None)

    def set(self, other):
        """
        Copy the given node.
        """
        self.key = other.key
        self.data = other.data[:]

    def __str__(self):
        return str((self.key, self.data))

    def __repr__(self):
        return str(self)


class BST:
    """
    A basic binary search tree in pure Python, used
    as an engine for indexing.

    Parameters
    ----------
    data : Table
        Sorted columns of the original table
    row_index : Column object
        Row numbers corresponding to data columns
    unique : bool
        Whether the values of the index must be unique.
        Defaults to False.
    """

    NodeClass = Node

    def __init__(self, data, row_index, unique=False):
        """
        Initialize a Trie with given data and row indices.
        
        Args:
        data (list): A list of keys to be inserted into the Trie.
        row_index (list): A list of corresponding row indices for each key.
        unique (bool, optional): If True, ensures that all keys are unique. Defaults to False.
        
        Returns:
        None: The function does not return anything but initializes the Trie structure.
        
        This method sets up the Trie by inserting each key from the `data`
        """

        self.root = None
        self.size = 0
        self.unique = unique
        for key, row in zip(data, row_index):
            self.add(tuple(key), row)

    def add(self, key, data=None):
        """
        Add a key, data pair.
        """
        if data is None:
            data = key

        self.size += 1
        node = self.NodeClass(key, data)
        curr_node = self.root
        if curr_node is None:
            self.root = node
            return
        while True:
            if node < curr_node:
                if curr_node.left is None:
                    curr_node.left = node
                    break
                curr_node = curr_node.left
            elif node > curr_node:
                if curr_node.right is None:
                    curr_node.right = node
                    break
                curr_node = curr_node.right
            elif self.unique:
                raise ValueError("Cannot insert non-unique value")
            else:  # add data to node
                curr_node.data.extend(node.data)
                curr_node.data = sorted(curr_node.data)
                return

    def find(self, key):
        """
        Return all data values corresponding to a given key.

        Parameters
        ----------
        key : tuple
            Input key

        Returns
        -------
        data_vals : list
            List of rows corresponding to the input key
        """
        node, parent = self.find_node(key)
        return node.data if node is not None else []

    def find_node(self, key):
        """
        Find the node associated with the given key.
        """
        if self.root is None:
            return (None, None)
        return self._find_recursive(key, self.root, None)

    def shift_left(self, row):
        """
        Decrement all rows larger than the given row.
        """
        for node in self.traverse():
            node.data = [x - 1 if x > row else x for x in node.data]

    def shift_right(self, row):
        """
        Increment all rows greater than or equal to the given row.
        """
        for node in self.traverse():
            node.data = [x + 1 if x >= row else x for x in node.data]

    def _find_recursive(self, key, node, parent):
        """
        Finds a node with the given key in a binary search tree.
        
        Args:
        key: The key to search for in the tree.
        node: The current node being examined during the search.
        parent: The parent of the current node.
        
        Returns:
        A tuple containing the found node and its parent, or (None, None) if the key is not found.
        
        Raises:
        TypeError: If the key is of an incorrect type.
        
        Important Functions:
        - _
        """

        try:
            if key == node.key:
                return (node, parent)
            elif key > node.key:
                if node.right is None:
                    return (None, None)
                return self._find_recursive(key, node.right, node)
            else:
                if node.left is None:
                    return (None, None)
                return self._find_recursive(key, node.left, node)
        except TypeError:  # wrong key type
            return (None, None)

    def traverse(self, order="inorder"):
        """
        Return nodes of the BST in the given order.

        Parameters
        ----------
        order : str
            The order in which to recursively search the BST.
            Possible values are:
            "preorder": current node, left subtree, right subtree
            "inorder": left subtree, current node, right subtree
            "postorder": left subtree, right subtree, current node
        """
        if order == "preorder":
            return self._preorder(self.root, [])
        elif order == "inorder":
            return self._inorder(self.root, [])
        elif order == "postorder":
            return self._postorder(self.root, [])
        raise ValueError(f'Invalid traversal method: "{order}"')

    def items(self):
        """
        Return BST items in order as (key, data) pairs.
        """
        return [(x.key, x.data) for x in self.traverse()]

    def sort(self):
        """
        Make row order align with key order.
        """
        i = 0
        for node in self.traverse():
            num_rows = len(node.data)
            node.data = [x for x in range(i, i + num_rows)]
            i += num_rows

    def sorted_data(self):
        """
        Return BST rows sorted by key values.
        """
        return [x for node in self.traverse() for x in node.data]

    def _preorder(self, node, lst):
        """
        Preorders a binary tree.
        
        Args:
        node (Node): The root node of the binary tree.
        lst (list): A list to store the preordered nodes.
        
        Returns:
        list: A list of nodes in preordered traversal order.
        
        This function performs a preorder traversal of a binary tree, appending each visited node to the given list. It recursively traverses the left and right subtrees after visiting the current node.
        """

        if node is None:
            return lst
        lst.append(node)
        self._preorder(node.left, lst)
        self._preorder(node.right, lst)
        return lst

    def _inorder(self, node, lst):
        """
        In-order traversal of a binary tree.
        
        Args:
        node (TreeNode): The root node of the binary tree.
        lst (list[TreeNode]): A list to store the nodes in in-order.
        
        Returns:
        list[TreeNode]: The list of nodes in in-order.
        
        This function performs an in-order traversal of a binary tree, appending each node to the given list in the order of left subtree, root, right subtree. It uses recursion to traverse the tree.
        """

        if node is None:
            return lst
        self._inorder(node.left, lst)
        lst.append(node)
        self._inorder(node.right, lst)
        return lst

    def _postorder(self, node, lst):
        """
        Postorder traversal of a binary tree.
        
        Args:
        node (TreeNode): The root node of the binary tree.
        lst (list): An empty list to store the nodes in postorder.
        
        Returns:
        list: A list of nodes in postorder.
        
        This function performs a postorder traversal of a binary tree, appending each node to the given list in the order they are visited. It uses recursion to traverse the left and right subtrees before adding the current node to the list
        """

        if node is None:
            return lst
        self._postorder(node.left, lst)
        self._postorder(node.right, lst)
        lst.append(node)
        return lst

    def _substitute(self, node, parent, new_node):
        """
        Substitutes a given node with a new node in the tree.
        
        Args:
        node (Node): The node to be replaced.
        parent (Node): The parent of the node to be replaced.
        new_node (Node): The new node that will replace the old one.
        
        This method updates the tree structure by replacing an existing node with a new one. If the node being replaced is the root, the root is updated to point to the new node. Otherwise, the parent node
        """

        if node is self.root:
            self.root = new_node
        else:
            parent.replace(node, new_node)

    def remove(self, key, data=None):
        """
        Remove data corresponding to the given key.

        Parameters
        ----------
        key : tuple
            The key to remove
        data : int or None
            If None, remove the node corresponding to the given key.
            If not None, remove only the given data value from the node.

        Returns
        -------
        successful : bool
            True if removal was successful, false otherwise
        """
        node, parent = self.find_node(key)
        if node is None:
            return False
        if data is not None:
            if data not in node.data:
                raise ValueError("Data does not belong to correct node")
            elif len(node.data) > 1:
                node.data.remove(data)
                return True
        if node.left is None and node.right is None:
            self._substitute(node, parent, None)
        elif node.left is None and node.right is not None:
            self._substitute(node, parent, node.right)
        elif node.right is None and node.left is not None:
            self._substitute(node, parent, node.left)
        else:
            # find largest element of left subtree
            curr_node = node.left
            parent = node
            while curr_node.right is not None:
                parent = curr_node
                curr_node = curr_node.right
            self._substitute(curr_node, parent, curr_node.left)
            node.set(curr_node)
        self.size -= 1
        return True

    def is_valid(self):
        """
        Returns whether this is a valid BST.
        """
        return self._is_valid(self.root)

    def _is_valid(self, node):
        """
        Determines if a given binary tree node is valid based on specific conditions.
        
        Args:
        node (TreeNode): The current node being evaluated.
        
        Returns:
        bool: True if the node satisfies the validity conditions, False otherwise.
        
        Conditions:
        - If the node is None, it is considered valid.
        - For a non-None node, its left child must be less than or equal to the node value,
        and its right child must be greater than or equal to the node
        """

        if node is None:
            return True
        return (
            (node.left is None or node.left <= node)
            and (node.right is None or node.right >= node)
            and self._is_valid(node.left)
            and self._is_valid(node.right)
        )

    def range(self, lower, upper, bounds=(True, True)):
        """
        Return all nodes with keys in the given range.

        Parameters
        ----------
        lower : tuple
            Lower bound
        upper : tuple
            Upper bound
        bounds : (2,) tuple of bool
            Indicates whether the search should be inclusive or
            exclusive with respect to the endpoints. The first
            argument corresponds to an inclusive lower bound,
            and the second argument to an inclusive upper bound.
        """
        nodes = self.range_nodes(lower, upper, bounds)
        return [x for node in nodes for x in node.data]

    def range_nodes(self, lower, upper, bounds=(True, True)):
        """
        Return nodes in the given range.
        """
        if self.root is None:
            return []
        # op1 is <= or <, op2 is >= or >
        op1 = operator.le if bounds[0] else operator.lt
        op2 = operator.ge if bounds[1] else operator.gt
        return self._range(lower, upper, op1, op2, self.root, [])

    def same_prefix(self, val):
        """
        Assuming the given value has smaller length than keys, return
        nodes whose keys have this value as a prefix.
        """
        if self.root is None:
            return []
        nodes = self._same_prefix(val, self.root, [])
        return [x for node in nodes for x in node.data]

    def _range(self, lower, upper, op1, op2, node, lst):
        """
        Finds nodes within a specified range in a binary search tree.
        
        Args:
        lower (int): The lower bound of the range.
        upper (int): The upper bound of the range.
        op1 (function): A comparison function to check if the node key is greater than or equal to the lower bound.
        op2 (function): A comparison function to check if the node key is less than or equal to the upper bound.
        node (Node): The current node being processed
        """

        if op1(lower, node.key) and op2(upper, node.key):
            lst.append(node)
        if upper > node.key and node.right is not None:
            self._range(lower, upper, op1, op2, node.right, lst)
        if lower < node.key and node.left is not None:
            self._range(lower, upper, op1, op2, node.left, lst)
        return lst

    def _same_prefix(self, val, node, lst):
        """
        Finds nodes with keys that have the same prefix as the given value.
        
        Args:
        val (str): The value to compare prefixes with.
        node (Node): The current node in the tree traversal.
        lst (list): A list to store nodes with matching prefixes.
        
        Returns:
        list: A list of nodes whose keys share the same prefix as `val`.
        
        This function recursively traverses a binary search tree to find all nodes
        whose keys start with the same prefix
        """

        prefix = node.key[: len(val)]
        if prefix == val:
            lst.append(node)
        if prefix <= val and node.right is not None:
            self._same_prefix(val, node.right, lst)
        if prefix >= val and node.left is not None:
            self._same_prefix(val, node.left, lst)
        return lst

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def _print(self, node, level):
        """
        Prints the tree in a formatted manner.
        
        Args:
        node (Node): The root node of the tree to be printed.
        level (int): The current level of indentation.
        
        Returns:
        str: A string representation of the tree, with each level indented appropriately.
        """

        line = "\t" * level + str(node) + "\n"
        if node.left is not None:
            line += self._print(node.left, level + 1)
        if node.right is not None:
            line += self._print(node.right, level + 1)
        return line

    @property
    def height(self):
        """
        Return the BST height.
        """
        return self._height(self.root)

    def _height(self, node):
        """
        Calculate the height of a binary tree.
        
        Args:
        node (TreeNode): The root node of the binary tree.
        
        Returns:
        int: The height of the binary tree.
        
        This function recursively calculates the height of a binary tree by finding the maximum height between the left and right subtrees and adding one for the current node. If the node is None, it returns -1.
        """

        if node is None:
            return -1
        return max(self._height(node.left), self._height(node.right)) + 1

    def replace_rows(self, row_map):
        """
        Replace all rows with the values they map to in the
        given dictionary. Any rows not present as keys in
        the dictionary will have their nodes deleted.

        Parameters
        ----------
        row_map : dict
            Mapping of row numbers to new row numbers
        """
        for key, data in self.items():
            data[:] = [row_map[x] for x in data if x in row_map]
