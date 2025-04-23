import numpy as np
from numpy.testing import assert_array_equal
import pytest

from sklearn.feature_extraction import FeatureHasher
from sklearn.feature_extraction._hashing_fast import transform as _hashing_transform


def test_feature_hasher_dicts():
    """
    Test the functionality of the FeatureHasher with dictionaries.
    
    This function tests the FeatureHasher's ability to handle input data in the form of dictionaries. It verifies that the input type is correctly identified as 'dict' and checks the transformation of raw dictionary data into a feature matrix. Additionally, it ensures that the transformation remains consistent when the input type is explicitly set to 'pair' and the data is provided as an iterator of dictionary item pairs.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key
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
    """
    Test the FeatureHasher with pairs of features.
    
    This function tests the FeatureHasher on a set of input data where each data point is a dictionary of key-value pairs. The FeatureHasher is configured to use 16 features and expects the input to be in the form of key-value pairs. The function checks the output of the FeatureHasher by comparing the non-zero values in the transformed data.
    
    Parameters:
    raw_X (iterable of dict): An iterable of dictionaries, where each
    """

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
"
    ).fit_transform(X)
    assert Xt.data[0] == len(X[0])
