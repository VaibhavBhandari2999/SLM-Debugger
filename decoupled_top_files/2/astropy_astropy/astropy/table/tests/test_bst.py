# Licensed under a 3-clause BSD style license - see LICENSE.rst

import pytest

from astropy.table.bst import BST


def get_tree(TreeType):
    """
    Create a binary search tree (BST) with specified values.
    
    Args:
    TreeType (class): A class representing a binary search tree.
    
    Returns:
    TreeType: An instance of the specified binary search tree class containing the values [5, 2, 9, 3, 4, 1, 6, 10, 8, 7].
    
    Example:
    >>> from binary_search_tree import BinarySearchTree
    >>> bst = get_tree(BinarySearchTree
    """

    b = TreeType([], [])
    for val in [5, 2, 9, 3, 4, 1, 6, 10, 8, 7]:
        b.add(val)
    return b


@pytest.fixture
def tree():
    """
    5
    /   \
    2     9
    / \   / \
    1   3 6  10
    \ \
    4  8
    /
    7
    """

    return get_tree(BST)
    r"""
         5
       /   \
      2     9
     / \   / \
    1   3 6  10
         \ \
         4  8
           /
          7
    """


@pytest.fixture
def bst(tree):
    return tree


def test_bst_add(bst):
    """
    Test the BST add method.
    
    Args:
    bst (BinarySearchTree): The binary search tree instance to be tested.
    
    Summary:
    This function tests the add method of a binary search tree (BST) by adding elements to the tree and verifying that the structure and data of the tree are correct. It checks if the root node contains the value 5, and its left and right children contain the values 2 and 9 respectively. It also verifies that the left and right children of the
    """

    root = bst.root
    assert root.data == [5]
    assert root.left.data == [2]
    assert root.right.data == [9]
    assert root.left.left.data == [1]
    assert root.left.right.data == [3]
    assert root.right.left.data == [6]
    assert root.right.right.data == [10]
    assert root.left.right.right.data == [4]
    assert root.right.left.right.data == [8]
    assert root.right.left.right.left.data == [7]


def test_bst_dimensions(bst):
    assert bst.size == 10
    assert bst.height == 4


def test_bst_find(tree):
    """
    Test the find method of a Binary Search Tree (BST).
    
    Args:
    tree (BinarySearchTree): The BST instance to be tested.
    
    Summary:
    This function tests the find method of a Binary Search Tree by searching for integers from 1 to 10, an empty value (0), and a non-existent value ("1"). It asserts that the returned nodes match the expected results.
    
    Important Functions:
    - find: The method being tested, which searches for a given value in
    """

    bst = tree
    for i in range(1, 11):
        node = bst.find(i)
        assert node == [i]
    assert bst.find(0) == []
    assert bst.find(11) == []
    assert bst.find("1") == []


def test_bst_traverse(bst):
    """
    Test the traversal methods of a Binary Search Tree (BST).
    
    Args:
    bst (BinarySearchTree): The binary search tree to be tested.
    
    This function tests the preorder, inorder, and postorder traversal methods of a BST by comparing the generated traversal results with expected values. It uses the `traverse` method of the BST to generate the traversal lists and asserts that they match the expected results.
    
    Expected Results:
    - Preorder Traversal: [5, 2, 1
    """

    preord = [5, 2, 1, 3, 4, 9, 6, 8, 7, 10]
    inord = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    postord = [1, 4, 3, 2, 7, 8, 6, 10, 9, 5]
    traversals = {}
    for order in ("preorder", "inorder", "postorder"):
        traversals[order] = [x.key for x in bst.traverse(order)]
    assert traversals["preorder"] == preord
    assert traversals["inorder"] == inord
    assert traversals["postorder"] == postord


def test_bst_remove(bst):
    """
    Test the removal of nodes from a Binary Search Tree (BST).
    
    Args:
    bst (BinarySearchTree): The Binary Search Tree to be tested.
    
    This function tests the removal of nodes from a BST by iterating over a predefined sequence of values. It checks if the removal operation is successful, verifies the validity of the tree after each removal, ensures the correct order of traversal, and confirms the updated size of the tree.
    
    Important Functions:
    - `bst.remove(val)`: Removes a node
    """

    order = (6, 9, 1, 3, 7, 2, 10, 5, 4, 8)
    vals = set(range(1, 11))
    for i, val in enumerate(order):
        assert bst.remove(val) is True
        assert bst.is_valid()
        assert {x.key for x in bst.traverse("inorder")} == vals.difference(
            order[: i + 1]
        )
        assert bst.size == 10 - i - 1
        assert bst.remove(-val) is False


def test_bst_duplicate(bst):
    """
    Test the behavior of a Binary Search Tree (BST) when adding, finding, removing nodes, and handling duplicates.
    
    Args:
    bst (BinarySearchTree): The Binary Search Tree instance to be tested.
    
    Methods:
    add: Adds a node with a given key and value to the BST.
    find: Searches for a node with a given key in the BST.
    remove: Removes a node with a given key from the BST.
    
    Raises:
    ValueError: If the specified data does
    """

    bst.add(10, 11)
    assert bst.find(10) == [10, 11]
    assert bst.remove(10, data=10) is True
    assert bst.find(10) == [11]
    with pytest.raises(ValueError):
        bst.remove(10, data=30)  # invalid data
    assert bst.remove(10) is True
    assert bst.remove(10) is False


def test_bst_range(tree):
    """
    Tests the range_nodes method of a Binary Search Tree (BST).
    
    Args:
    tree (BinarySearchTree): The BST to be tested.
    
    Returns:
    None
    
    Summary:
    This function tests the range_nodes method of a Binary Search Tree (BST). It checks if the method correctly returns nodes within a specified key range. The range_nodes method is called with different key ranges and the returned nodes are compared against expected results using assertions.
    """

    bst = tree
    lst = bst.range_nodes(4, 8)
    assert sorted(x.key for x in lst) == [4, 5, 6, 7, 8]
    lst = bst.range_nodes(10, 11)
    assert [x.key for x in lst] == [10]
    lst = bst.range_nodes(11, 20)
    assert len(lst) == 0
