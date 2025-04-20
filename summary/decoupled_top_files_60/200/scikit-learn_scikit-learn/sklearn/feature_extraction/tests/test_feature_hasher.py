
import numpy as np
from numpy.testing import assert_array_equal
import pytest

from sklearn.feature_extraction import FeatureHasher
from sklearn.utils.testing import (ignore_warnings,
                                   fails_if_pypy)

pytestmark = fails_if_pypy


def test_feature_hasher_dicts():
    """
    Test the functionality of the FeatureHasher with dictionaries.
    
    This function tests the FeatureHasher's ability to handle dictionaries as input.
    It verifies that the input type is correctly identified as 'dict' and checks the
    output of the transformer when applied to a list of dictionaries and a generator
    of item pairs. The test ensures that the output is consistent regardless of the
    input type provided to the transformer.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Parameters:
    - `n_features`:
    """

    h = FeatureHasher(n_features=16)
    assert "dict" == h.input_type

    raw_X = [{"foo": "bar", "dada": 42, "tzara": 37},
             {"foo": "baz", "gaga": "string1"}]
    X1 = FeatureHasher(n_features=16).transform(raw_X)
    gen = (iter(d.items()) for d in raw_X)
    X2 = FeatureHasher(n_features=16, input_type="pair").transform(gen)
    assert_array_equal(X1.toarray(), X2.toarray())


def test_feature_hasher_strings():
    # mix byte and Unicode strings; note that "foo" is a duplicate in row 0
    raw_X = [["foo", "bar", "baz", "foo".encode("ascii")],
             ["bar".encode("ascii"), "baz", "quux"]]

    for lg_n_features in (7, 9, 11, 16, 22):
        n_features = 2 ** lg_n_features

        it = (x for x in raw_X)                 # iterable

        h = FeatureHasher(n_features, input_type="string",
                          alternate_sign=False)
        X = h.transform(it)

        assert X.shape[0] == len(raw_X)
        assert X.shape[1] == n_features

        assert X[0].sum() == 4
        assert X[1].sum() == 3

        assert X.nnz == 6


def test_feature_hasher_pairs():
    raw_X = (iter(d.items()) for d in [{"foo": 1, "bar": 2},
                                       {"baz": 3, "quux": 4, "foo": -1}])
    h = FeatureHasher(n_features=16, input_type="pair")
    x1, x2 = h.transform(raw_X).toarray()
    x1_nz = sorted(np.abs(x1[x1 != 0]))
    x2_nz = sorted(np.abs(x2[x2 != 0]))
    assert [1, 2] == x1_nz
    assert [1, 3, 4] == x2_nz


def test_feature_hasher_pairs_with_string_values():
    """
    Test the FeatureHasher with string values in pair format.
    
    This function tests the FeatureHasher on a set of input data where each
    data point is a dictionary with string keys and values. The FeatureHasher
    is configured to use 16 features and to interpret the input as pairs of
    keys and values.
    
    Parameters:
    raw_X (iterable): An iterable of dictionaries, where each dictionary
    contains string keys and values. The dictionaries represent data
    points for transformation.
    """

    raw_X = (iter(d.items()) for d in [{"foo": 1, "bar": "a"},
                                       {"baz": "abc", "quux": 4, "foo": -1}])
    h = FeatureHasher(n_features=16, input_type="pair")
    x1, x2 = h.transform(raw_X).toarray()
    x1_nz = sorted(np.abs(x1[x1 != 0]))
    x2_nz = sorted(np.abs(x2[x2 != 0]))
    assert [1, 1] == x1_nz
    assert [1, 1, 4] == x2_nz

    raw_X = (iter(d.items()) for d in [{"bax": "abc"},
                                       {"bax": "abc"}])
    x1, x2 = h.transform(raw_X).toarray()
    x1_nz = np.abs(x1[x1 != 0])
    x2_nz = np.abs(x2[x2 != 0])
    assert [1] == x1_nz
    assert [1] == x2_nz
    assert_array_equal(x1, x2)


def test_hash_empty_input():
    """
    test_hash_empty_input
    ---------------------
    This function tests the hashing of an empty input using the FeatureHasher.
    
    Parameters
    ----------
    n_features : int
    The number of features to use for hashing.
    raw_X : list
    A list containing empty lists, empty tuples, and an empty iterator to be hashed.
    
    Returns
    -------
    X : scipy.sparse.csr_matrix
    The hashed output as a sparse matrix.
    
    Assertions
    ----------
    - The output matrix should be of shape (len(raw_X
    """

    n_features = 16
    raw_X = [[], (), iter(range(0))]

    h = FeatureHasher(n_features=n_features, input_type="string")
    X = h.transform(raw_X)

    assert_array_equal(X.A, np.zeros((len(raw_X), n_features)))


def test_hasher_invalid_input():
    with pytest.raises(ValueError):
        FeatureHasher(input_type="gobbledygook")
    with pytest.raises(ValueError):
        FeatureHasher(n_features=-1)
    with pytest.raises(ValueError):
        FeatureHasher(n_features=0)
    with pytest.raises(TypeError):
        FeatureHasher(n_features='ham')

    h = FeatureHasher(n_features=np.uint16(2 ** 6))
    with pytest.raises(ValueError):
        h.transform([])
    with pytest.raises(Exception):
        h.transform([[5.5]])
    with pytest.raises(Exception):
        h.transform([[None]])


def test_hasher_set_params():
    # Test delayed input validation in fit (useful for grid search).
    hasher = FeatureHasher()
    hasher.set_params(n_features=np.inf)
    with pytest.raises(TypeError):
        hasher.fit()


def test_hasher_zeros():
    """
    Test that the FeatureHasher does not materialize zeros.
    
    This function checks that when a feature with a value of zero is passed to
    the FeatureHasher, it does not appear in the output matrix. The input is a
    dictionary with a single feature 'foo' having a value of 0. The output is a
    scipy sparse matrix, and the assertion checks that the number of non-zero
    elements in the output is 0.
    
    Parameters:
    None
    
    Returns:
    None
    
    Assertions
    """

    # Assert that no zeros are materialized in the output.
    X = FeatureHasher().transform([{'foo': 0}])
    assert X.data.shape == (0,)


@ignore_warnings(category=DeprecationWarning)
def test_hasher_alternate_sign():
    X = [list("Thequickbrownfoxjumped")]

    Xt = FeatureHasher(alternate_sign=True,
                       input_type='string').fit_transform(X)
    assert Xt.data.min() < 0 and Xt.data.max() > 0

    Xt = FeatureHasher(alternate_sign=False,
                       input_type='string').fit_transform(X)
    assert Xt.data.min() > 0


def test_hash_collisions():
    X = [list("Thequickbrownfoxjumped")]

    Xt = FeatureHasher(alternate_sign=True, n_features=1,
                       input_type='string').fit_transform(X)
    # check that some of the hashed tokens are added
    # with an opposite sign and cancel out
    assert abs(Xt.data[0]) < len(X[0])

    Xt = FeatureHasher(alternate_sign=False, n_features=1,
                       input_type='string').fit_transform(X)
    assert Xt.data[0] == len(X[0])
sform(X)
    assert Xt.data[0] == len(X[0])
