
import numpy as np
from numpy.testing import assert_array_equal

from sklearn.feature_extraction import FeatureHasher
from sklearn.utils.testing import (assert_raises, assert_equal,
                                   ignore_warnings, fails_if_pypy)

pytestmark = fails_if_pypy


def test_feature_hasher_dicts():
    """
    Test the FeatureHasher with dictionaries as input.
    
    Parameters
    ----------
    raw_X : list of dictionaries
    A list where each element is a dictionary containing the features.
    
    Returns
    -------
    X1, X2 : scipy.sparse.csr_matrix
    Two sparse matrices with the same feature representation, obtained using
    two different methods of input provision to FeatureHasher.
    X1 is obtained by directly passing a list of dictionaries, while X2 is
    obtained by passing an iterator of item pairs
    """

    h = FeatureHasher(n_features=16)
    assert_equal("dict", h.input_type)

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

        assert_equal(X.shape[0], len(raw_X))
        assert_equal(X.shape[1], n_features)

        assert_equal(X[0].sum(), 4)
        assert_equal(X[1].sum(), 3)

        assert_equal(X.nnz, 6)


def test_feature_hasher_pairs():
    raw_X = (iter(d.items()) for d in [{"foo": 1, "bar": 2},
                                       {"baz": 3, "quux": 4, "foo": -1}])
    h = FeatureHasher(n_features=16, input_type="pair")
    x1, x2 = h.transform(raw_X).toarray()
    x1_nz = sorted(np.abs(x1[x1 != 0]))
    x2_nz = sorted(np.abs(x2[x2 != 0]))
    assert_equal([1, 2], x1_nz)
    assert_equal([1, 3, 4], x2_nz)


def test_feature_hasher_pairs_with_string_values():
    """
    Test the FeatureHasher with string values in pair format.
    
    This function tests the FeatureHasher's ability to handle string values in pair format. It uses a generator to create a sequence of dictionaries, each containing string and numeric values. The FeatureHasher is configured to use 16 features and to process the data as pairs. The transformed data is then converted to a dense array and the non-zero values are extracted and sorted. The function asserts that the sorted non-zero values match the expected output
    """

    raw_X = (iter(d.items()) for d in [{"foo": 1, "bar": "a"},
                                       {"baz": "abc", "quux": 4, "foo": -1}])
    h = FeatureHasher(n_features=16, input_type="pair")
    x1, x2 = h.transform(raw_X).toarray()
    x1_nz = sorted(np.abs(x1[x1 != 0]))
    x2_nz = sorted(np.abs(x2[x2 != 0]))
    assert_equal([1, 1], x1_nz)
    assert_equal([1, 1, 4], x2_nz)

    raw_X = (iter(d.items()) for d in [{"bax": "abc"},
                                       {"bax": "abc"}])
    x1, x2 = h.transform(raw_X).toarray()
    x1_nz = np.abs(x1[x1 != 0])
    x2_nz = np.abs(x2[x2 != 0])
    assert_equal([1], x1_nz)
    assert_equal([1], x2_nz)
    assert_array_equal(x1, x2)


def test_hash_empty_input():
    """
    Test the FeatureHasher with an empty input.
    
    Parameters:
    n_features (int): The number of features to hash to.
    raw_X (list): A list containing empty lists, empty tuples, and an empty iterator.
    
    Returns:
    X (scipy.sparse.csr_matrix): A sparse matrix with the hashed features, which should be all zeros due to the empty input.
    
    This function is used to verify that the FeatureHasher correctly handles empty inputs by producing a zero matrix of the
    """

    n_features = 16
    raw_X = [[], (), iter(range(0))]

    h = FeatureHasher(n_features=n_features, input_type="string")
    X = h.transform(raw_X)

    assert_array_equal(X.A, np.zeros((len(raw_X), n_features)))


def test_hasher_invalid_input():
    assert_raises(ValueError, FeatureHasher, input_type="gobbledygook")
    assert_raises(ValueError, FeatureHasher, n_features=-1)
    assert_raises(ValueError, FeatureHasher, n_features=0)
    assert_raises(TypeError, FeatureHasher, n_features='ham')

    h = FeatureHasher(n_features=np.uint16(2 ** 6))
    assert_raises(ValueError, h.transform, [])
    assert_raises(Exception, h.transform, [[5.5]])
    assert_raises(Exception, h.transform, [[None]])


def test_hasher_set_params():
    """
    Set the parameters of the FeatureHasher.
    
    This method allows for the modification of the FeatureHasher's parameters. However, it will raise a TypeError if called during the fit method, which is useful for scenarios like grid search where delayed input validation is required.
    
    Parameters:
    n_features (int or None): The number of features to use. If set to None, the number of features will be determined by the input data. If set to np.inf, it will use an infinite number of features
    """

    # Test delayed input validation in fit (useful for grid search).
    hasher = FeatureHasher()
    hasher.set_params(n_features=np.inf)
    assert_raises(TypeError, hasher.fit)


def test_hasher_zeros():
    # Assert that no zeros are materialized in the output.
    X = FeatureHasher().transform([{'foo': 0}])
    assert_equal(X.data.shape, (0,))


@ignore_warnings(category=DeprecationWarning)
def test_hasher_alternate_sign():
    """
    Generate feature hashes for input strings using the FeatureHasher.
    
    This function hashes input strings into a fixed-size vector using the FeatureHasher. The alternate_sign parameter determines the sign of the hash values.
    
    Parameters:
    X (list of str): The input list of strings to be hashed.
    
    Keyword Arguments:
    alternate_sign (bool): If True, the hash values will alternate in sign. If False, all hash values will be positive. Default is True.
    input_type (str): The type
    """

    X = [list("Thequickbrownfoxjumped")]

    Xt = FeatureHasher(alternate_sign=True,
                       input_type='string').fit_transform(X)
    assert Xt.data.min() < 0 and Xt.data.max() > 0

    Xt = FeatureHasher(alternate_sign=False,
                       input_type='string').fit_transform(X)
    assert Xt.data.min() > 0


def test_hash_collisions():
    """
    Generate a Python docstring for the provided function.
    
    This function tests for hash collisions in feature hashing for string input. It uses the `FeatureHasher` class to transform a list of strings into a feature vector. The function checks whether the hashed tokens are added with opposite signs, which should result in some cancellation, or if they are added with the same sign, which should result in the sum of the lengths of the strings.
    
    Key Parameters:
    - `X`: A list of strings to be hashed
    """

    X = [list("Thequickbrownfoxjumped")]

    Xt = FeatureHasher(alternate_sign=True, n_features=1,
                       input_type='string').fit_transform(X)
    # check that some of the hashed tokens are added
    # with an opposite sign and cancel out
    assert abs(Xt.data[0]) < len(X[0])

    Xt = FeatureHasher(alternate_sign=False, n_features=1,
                       input_type='string').fit_transform(X)
    assert Xt.data[0] == len(X[0])
