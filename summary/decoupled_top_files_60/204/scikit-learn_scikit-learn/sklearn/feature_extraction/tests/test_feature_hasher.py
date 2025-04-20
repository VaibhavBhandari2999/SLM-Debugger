import numpy as np
from numpy.testing import assert_array_equal
import pytest

from sklearn.feature_extraction import FeatureHasher
from sklearn.feature_extraction._hashing_fast import transform as _hashing_transform


def test_feature_hasher_dicts():
    """
    Tests the functionality of the FeatureHasher with dictionaries as input.
    
    This function verifies that the FeatureHasher correctly processes dictionaries and generates the expected output. It compares the results of using dictionaries directly and using an iterator of item pairs from dictionaries.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Parameters:
    - feature_hasher: An instance of the FeatureHasher class with `n_features` set to 16.
    - raw_X: A list of dictionaries containing string and numeric data
    """

    feature_hasher = FeatureHasher(n_features=16)
    assert "dict" == feature_hasher.input_type

    raw_X = [{"foo": "bar", "dada": 42, "tzara": 37}, {"foo": "baz", "gaga": "string1"}]
    X1 = FeatureHasher(n_features=16).transform(raw_X)
    gen = (iter(d.items()) for d in raw_X)
    X2 = FeatureHasher(n_features=16, input_type="pair").transform(gen)
    assert_array_equal(X1.toarray(), X2.toarray())


def test_feature_hasher_strings():
    # mix byte and Unicode strings; note that "foo" is a duplicate in row 0
    raw_X = [
        ["foo", "bar", "baz", "foo".encode("ascii")],
        ["bar".encode("ascii"), "baz", "quux"],
    ]

    for lg_n_features in (7, 9, 11, 16, 22):
        n_features = 2**lg_n_features

        it = (x for x in raw_X)  # iterable

        feature_hasher = FeatureHasher(
            n_features=n_features, input_type="string", alternate_sign=False
        )
        X = feature_hasher.transform(it)

        assert X.shape[0] == len(raw_X)
        assert X.shape[1] == n_features

        assert X[0].sum() == 4
        assert X[1].sum() == 3

        assert X.nnz == 6


@pytest.mark.parametrize(
    "raw_X",
    [
        ["my_string", "another_string"],
        (x for x in ["my_string", "another_string"]),
    ],
    ids=["list", "generator"],
)
def test_feature_hasher_single_string(raw_X):
    """FeatureHasher raises error when a sample is a single string.

    Non-regression test for gh-13199.
    """
    msg = "Samples can not be a single string"

    feature_hasher = FeatureHasher(n_features=10, input_type="string")
    with pytest.raises(ValueError, match=msg):
        feature_hasher.transform(raw_X)


def test_hashing_transform_seed():
    # check the influence of the seed when computing the hashes
    raw_X = [
        ["foo", "bar", "baz", "foo".encode("ascii")],
        ["bar".encode("ascii"), "baz", "quux"],
    ]

    raw_X_ = (((f, 1) for f in x) for x in raw_X)
    indices, indptr, _ = _hashing_transform(raw_X_, 2**7, str, False)

    raw_X_ = (((f, 1) for f in x) for x in raw_X)
    indices_0, indptr_0, _ = _hashing_transform(raw_X_, 2**7, str, False, seed=0)
    assert_array_equal(indices, indices_0)
    assert_array_equal(indptr, indptr_0)

    raw_X_ = (((f, 1) for f in x) for x in raw_X)
    indices_1, _, _ = _hashing_transform(raw_X_, 2**7, str, False, seed=1)
    with pytest.raises(AssertionError):
        assert_array_equal(indices, indices_1)


def test_feature_hasher_pairs():
    raw_X = (
        iter(d.items())
        for d in [{"foo": 1, "bar": 2}, {"baz": 3, "quux": 4, "foo": -1}]
    )
    feature_hasher = FeatureHasher(n_features=16, input_type="pair")
    x1, x2 = feature_hasher.transform(raw_X).toarray()
    x1_nz = sorted(np.abs(x1[x1 != 0]))
    x2_nz = sorted(np.abs(x2[x2 != 0]))
    assert [1, 2] == x1_nz
    assert [1, 3, 4] == x2_nz


def test_feature_hasher_pairs_with_string_values():
    """
    Test the FeatureHasher with string values in pairs.
    
    This function tests the FeatureHasher's ability to handle string values in pairs.
    It checks the transformation of a list of dictionaries with string and integer values.
    The FeatureHasher is configured with 16 features and expects pair input.
    
    Parameters:
    None
    
    Returns:
    None
    
    Assertions:
    - The non-zero values in the transformed array for the first set of data are [1, 1].
    - The non-zero values in
    """

    raw_X = (
        iter(d.items())
        for d in [{"foo": 1, "bar": "a"}, {"baz": "abc", "quux": 4, "foo": -1}]
    )
    feature_hasher = FeatureHasher(n_features=16, input_type="pair")
    x1, x2 = feature_hasher.transform(raw_X).toarray()
    x1_nz = sorted(np.abs(x1[x1 != 0]))
    x2_nz = sorted(np.abs(x2[x2 != 0]))
    assert [1, 1] == x1_nz
    assert [1, 1, 4] == x2_nz

    raw_X = (iter(d.items()) for d in [{"bax": "abc"}, {"bax": "abc"}])
    x1, x2 = feature_hasher.transform(raw_X).toarray()
    x1_nz = np.abs(x1[x1 != 0])
    x2_nz = np.abs(x2[x2 != 0])
    assert [1] == x1_nz
    assert [1] == x2_nz
    assert_array_equal(x1, x2)


def test_hash_empty_input():
    """
    Generate a feature hash matrix from an empty or null input.
    
    This function takes a list of empty or null inputs and transforms them into a feature hash matrix using the FeatureHasher. The FeatureHasher is initialized with a specified number of features and expects string inputs. When given empty or null inputs, the function should return a matrix where all feature values are zero.
    
    Parameters:
    n_features (int): The number of features to use in the hash matrix.
    raw_X (list): A list
    """

    n_features = 16
    raw_X = [[], (), iter(range(0))]

    feature_hasher = FeatureHasher(n_features=n_features, input_type="string")
    X = feature_hasher.transform(raw_X)

    assert_array_equal(X.A, np.zeros((len(raw_X), n_features)))


def test_hasher_zeros():
    # Assert that no zeros are materialized in the output.
    X = FeatureHasher().transform([{"foo": 0}])
    assert X.data.shape == (0,)


def test_hasher_alternate_sign():
    X = [list("Thequickbrownfoxjumped")]

    Xt = FeatureHasher(alternate_sign=True, input_type="string").fit_transform(X)
    assert Xt.data.min() < 0 and Xt.data.max() > 0

    Xt = FeatureHasher(alternate_sign=False, input_type="string").fit_transform(X)
    assert Xt.data.min() > 0


def test_hash_collisions():
    """
    Tests for hash collisions in FeatureHasher.
    
    This function checks the behavior of FeatureHasher when hashing a string with
    different settings for `alternate_sign` and `n_features`. It ensures that the
    hashing process correctly handles collisions by either canceling out or
    accumulating the hashed tokens.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Parameters:
    - `alternate_sign`: A boolean indicating whether to alternate the sign of
    hashed tokens. When `True`, tokens with opposite
    """

    X = [list("Thequickbrownfoxjumped")]

    Xt = FeatureHasher(
        alternate_sign=True, n_features=1, input_type="string"
    ).fit_transform(X)
    # check that some of the hashed tokens are added
    # with an opposite sign and cancel out
    assert abs(Xt.data[0]) < len(X[0])

    Xt = FeatureHasher(
        alternate_sign=False, n_features=1, input_type="string"
    ).fit_transform(X)
    assert Xt.data[0] == len(X[0])
