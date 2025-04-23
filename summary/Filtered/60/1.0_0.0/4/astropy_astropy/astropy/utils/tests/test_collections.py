# Licensed under a 3-clause BSD style license - see LICENSE.rst

import pytest

from ...tests.helper import raises

from .. import collections


@raises(TypeError)
def test_homogeneous_list():
    l = collections.HomogeneousList(int)
    l.append(5.0)


@raises(TypeError)
def test_homogeneous_list2():
    l = collections.HomogeneousList(int)
    l.extend([5.0])


def test_homogeneous_list3():
    """
    Test appending an integer to a HomogeneousList.
    
    This function creates a HomogeneousList with a specified type (int in this case), appends an integer to it, and asserts that the list contains the appended integer.
    
    Parameters:
    None
    
    Returns:
    None
    
    Keywords:
    None
    
    Raises:
    AssertionError: If the HomogeneousList does not contain the appended integer.
    """

    l = collections.HomogeneousList(int)
    l.append(5)
    assert l == [5]


def test_homogeneous_list4():
    """
    Test a homogeneous list with integer elements.
    
    This function checks the functionality of a homogeneous list that only accepts integers. It creates an instance of the HomogeneousList class, extends it with a single integer value, and asserts that the list contains the expected integer.
    
    Parameters:
    - None
    
    Returns:
    - None
    
    Assertions:
    - The list should contain the integer 5 after extending it with [5].
    """

    l = collections.HomogeneousList(int)
    l.extend([5])
    assert l == [5]


@raises(TypeError)
def test_homogeneous_list5():
    l = collections.HomogeneousList(int, [1, 2, 3])
    l[1] = 5.0


def test_homogeneous_list_setitem_works():
    """
    Test that setting an item in a HomogeneousList works as expected.
    
    Parameters:
    None
    
    Returns:
    None
    
    Keywords:
    l: The HomogeneousList to be modified. It is initialized with integers [1, 2, 3].
    
    Description:
    This function tests the behavior of the `__setitem__` method in the `HomogeneousList` class. It creates a `HomogeneousList` with initial values [1, 2, 3] and sets the
    """

    l = collections.HomogeneousList(int, [1, 2, 3])
    l[1] = 5
    assert l == [1, 5, 3]


def test_homogeneous_list_setitem_works_with_slice():
    l = collections.HomogeneousList(int, [1, 2, 3])
    l[0:1] = [10, 20, 30]
    assert l == [10, 20, 30, 2, 3]

    l[:] = [5, 4, 3]
    assert l == [5, 4, 3]

    l[::2] = [2, 1]
    assert l == [2, 4, 1]


def test_homogeneous_list_init_got_invalid_type():
    with pytest.raises(TypeError):
        collections.HomogeneousList(int, [1, 2., 3])


def test_homogeneous_list_works_with_generators():
    hl = collections.HomogeneousList(int, (i for i in range(3)))
    assert hl == [0, 1, 2]

    hl = collections.HomogeneousList(int)
    hl.extend(i for i in range(3))
    assert hl == [0, 1, 2]

    hl = collections.HomogeneousList(int)
    hl[0:1] = (i for i in range(3))
    assert hl == [0, 1, 2]

    hl = collections.HomogeneousList(int)
    hl += (i for i in range(3))
    assert hl == [0, 1, 2]
