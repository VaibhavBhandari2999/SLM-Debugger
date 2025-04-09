# -*- coding: utf-8 -*-
from __future__ import division

import re

import numpy as np
from scipy import sparse
import pytest

from sklearn.exceptions import NotFittedError
from sklearn.utils.testing import assert_array_equal
from sklearn.utils.testing import assert_equal
from sklearn.utils.testing import assert_raises
from sklearn.utils.testing import assert_raises_regex
from sklearn.utils.testing import assert_allclose
from sklearn.utils.testing import ignore_warnings
from sklearn.utils.testing import assert_warns
from sklearn.utils.testing import assert_warns_message
from sklearn.utils.testing import assert_no_warnings

from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import OrdinalEncoder


def toarray(a):
    """
    Converts an input to a NumPy array if possible.
    
    Parameters:
    a (array-like): Input data that may be converted to a NumPy array.
    
    Returns:
    numpy.ndarray: The input data converted to a NumPy array if it has a 'toarray' method; otherwise, returns the original input data as a NumPy array.
    
    Notes:
    - If the input `a` has a 'toarray' method, it is called to convert `a` to
    """

    if hasattr(a, "toarray"):
        a = a.toarray()
    return a


def test_one_hot_encoder_sparse():
    """
    Tests the functionality of the OneHotEncoder class from scikit-learn.
    
    This function tests various aspects of the OneHotEncoder class, including:
    - Fitting and transforming data with automatic discovery of maximum values.
    - Specifying the maximum value manually.
    - Specifying the maximum value per feature.
    - Handling out-of-bounds categorical features.
    - Raising errors for incorrect numbers of features in both fit and transform operations.
    - Handling exceptions for invalid initialization parameters.
    """

    # Test OneHotEncoder's fit and transform.
    X = [[3, 2, 1], [0, 1, 1]]
    enc = OneHotEncoder()
    with ignore_warnings(category=(DeprecationWarning, FutureWarning)):
        # discover max values automatically
        X_trans = enc.fit_transform(X).toarray()
        assert_equal(X_trans.shape, (2, 5))
        assert_array_equal(enc.active_features_,
                           np.where([1, 0, 0, 1, 0, 1, 1, 0, 1])[0])
        assert_array_equal(enc.feature_indices_, [0, 4, 7, 9])

        # check outcome
        assert_array_equal(X_trans,
                           [[0., 1., 0., 1., 1.],
                            [1., 0., 1., 0., 1.]])

    # max value given as 3
    # enc = assert_warns(DeprecationWarning, OneHotEncoder, n_values=4)
    enc = OneHotEncoder(n_values=4)
    with ignore_warnings(category=DeprecationWarning):
        X_trans = enc.fit_transform(X)
        assert_equal(X_trans.shape, (2, 4 * 3))
        assert_array_equal(enc.feature_indices_, [0, 4, 8, 12])

    # max value given per feature
    # enc = assert_warns(DeprecationWarning, OneHotEncoder, n_values=[3, 2, 2])
    enc = OneHotEncoder(n_values=[3, 2, 2])
    with ignore_warnings(category=DeprecationWarning):
        X = [[1, 0, 1], [0, 1, 1]]
        X_trans = enc.fit_transform(X)
        assert_equal(X_trans.shape, (2, 3 + 2 + 2))
        assert_array_equal(enc.n_values_, [3, 2, 2])
    # check that testing with larger feature works:
    X = np.array([[2, 0, 1], [0, 1, 1]])
    enc.transform(X)

    # test that an error is raised when out of bounds:
    X_too_large = [[0, 2, 1], [0, 1, 1]]
    assert_raises(ValueError, enc.transform, X_too_large)
    error_msg = r"unknown categorical feature present \[2\] during transform"
    assert_raises_regex(ValueError, error_msg, enc.transform, X_too_large)
    with ignore_warnings(category=DeprecationWarning):
        assert_raises(
            ValueError,
            OneHotEncoder(n_values=2).fit_transform, X)

    # test that error is raised when wrong number of features
    assert_raises(ValueError, enc.transform, X[:, :-1])

    # test that error is raised when wrong number of features in fit
    # with prespecified n_values
    with ignore_warnings(category=DeprecationWarning):
        assert_raises(ValueError, enc.fit, X[:, :-1])
    # test exception on wrong init param
    with ignore_warnings(category=DeprecationWarning):
        assert_raises(
            TypeError, OneHotEncoder(n_values=np.int).fit, X)

    enc = OneHotEncoder()
    # test negative input to fit
    with ignore_warnings(category=FutureWarning):
        assert_raises(ValueError, enc.fit, [[0], [-1]])

    # test negative input to transform
    with ignore_warnings(category=FutureWarning):
        enc.fit([[0], [1]])
    assert_raises(ValueError, enc.transform, [[0], [-1]])


def test_one_hot_encoder_dense():
    """
    Tests the functionality of the OneHotEncoder with dense output.
    
    This function verifies the behavior of the OneHotEncoder when `sparse=False`.
    It checks the transformation of input data `X` into one-hot encoded form,
    ensuring that the shape of the transformed data matches the expected output.
    The function also validates the active features, feature indices, and the
    resulting one-hot encoded matrix.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `
    """

    # check for sparse=False
    X = [[3, 2, 1], [0, 1, 1]]
    enc = OneHotEncoder(sparse=False)
    with ignore_warnings(category=(DeprecationWarning, FutureWarning)):
        # discover max values automatically
        X_trans = enc.fit_transform(X)
        assert_equal(X_trans.shape, (2, 5))
        assert_array_equal(enc.active_features_,
                           np.where([1, 0, 0, 1, 0, 1, 1, 0, 1])[0])
        assert_array_equal(enc.feature_indices_, [0, 4, 7, 9])

    # check outcome
    assert_array_equal(X_trans,
                       np.array([[0., 1., 0., 1., 1.],
                                 [1., 0., 1., 0., 1.]]))


def test_one_hot_encoder_deprecationwarnings():
    """
    Tests the deprecation warnings for the OneHotEncoder.
    
    This function checks the deprecation warnings for the OneHotEncoder when handling integer inputs, fitting, and transforming data. It also verifies that the deprecated attributes are properly handled and that specifying certain keyword arguments avoids these warnings. Additionally, it tests the behavior of OneHotEncoder with categorical string inputs.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `assert_warns`: Used to check if a specific warning
    """

    for X in [[[3, 2, 1], [0, 1, 1]],
              [[3., 2., 1.], [0., 1., 1.]]]:
        enc = OneHotEncoder()
        assert_warns_message(FutureWarning, "handling of integer",
                             enc.fit, X)
        enc = OneHotEncoder()
        assert_warns_message(FutureWarning, "handling of integer",
                             enc.fit_transform, X)

        # check it still works correctly as well
        with ignore_warnings(category=FutureWarning):
            X_trans = enc.fit_transform(X).toarray()
        res = [[0., 1., 0., 1., 1.],
               [1., 0., 1., 0., 1.]]
        assert_array_equal(X_trans, res)

        # check deprecated attributes
        assert_warns(DeprecationWarning, lambda: enc.active_features_)
        assert_warns(DeprecationWarning, lambda: enc.feature_indices_)
        assert_warns(DeprecationWarning, lambda: enc.n_values_)

        # check no warning is raised if keyword is specified
        enc = OneHotEncoder(categories='auto')
        assert_no_warnings(enc.fit, X)
        enc = OneHotEncoder(categories='auto')
        assert_no_warnings(enc.fit_transform, X)
        X_trans = enc.fit_transform(X).toarray()
        assert_array_equal(X_trans, res)

        # check there is also a warning if the default is passed
        enc = OneHotEncoder(n_values='auto', handle_unknown='ignore')
        assert_warns(DeprecationWarning, enc.fit, X)

    X = np.array([['cat1', 'cat2']], dtype=object).T
    enc = OneHotEncoder(categorical_features='all')
    assert_warns(DeprecationWarning, enc.fit, X)


def test_one_hot_encoder_force_new_behaviour():
    """
    Tests the behavior of the OneHotEncoder when forced to use new behavior.
    
    This function evaluates the OneHotEncoder's response to different scenarios,
    specifically focusing on how it handles non-sequential category ranges and
    the impact of setting the `categories` parameter to 'auto'.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `OneHotEncoder()`: Initializes the OneHotEncoder object.
    - `fit(X)`: Fits the encoder to the
    """

    # ambiguous integer case (non secutive range of categories)
    X = np.array([[1, 2]]).T
    X2 = np.array([[0, 1]]).T

    # without argument -> by default using legacy behaviour with warnings
    enc = OneHotEncoder()

    with ignore_warnings(category=FutureWarning):
        enc.fit(X)

    res = enc.transform(X2)
    exp = np.array([[0, 0], [1, 0]])
    assert_array_equal(res.toarray(), exp)

    # with explicit auto argument -> don't use legacy behaviour
    # (so will raise an error on unseen value within range)
    enc = OneHotEncoder(categories='auto')
    enc.fit(X)
    assert_raises(ValueError, enc.transform, X2)


def _run_one_hot(X, X2, cat):
    """
    Transforms categorical features using OneHotEncoder.
    
    This function takes two sets of data, `X` and `X2`, along with a list of
    categorical feature indices `cat`. It applies the OneHotEncoder to both
    datasets, fitting the encoder on `X` and transforming both `X` and `X2`
    accordingly. The transformed data is returned as `Xtr` and `X2tr`.
    
    Parameters:
    -----------
    X : array-like
    """

    # enc = assert_warns(
    #     DeprecationWarning,
    #     OneHotEncoder, categorical_features=cat)
    enc = OneHotEncoder(categorical_features=cat)
    with ignore_warnings(category=(DeprecationWarning, FutureWarning)):
        Xtr = enc.fit_transform(X)
    with ignore_warnings(category=(DeprecationWarning, FutureWarning)):
        X2tr = enc.fit(X).transform(X2)
    return Xtr, X2tr


def _check_one_hot(X, X2, cat, n_features):
    """
    Check if the given categorical data is one-hot encoded.
    
    This function takes two arrays `X` and `X2`, a boolean array `cat`, and an integer `n_features`. It checks if the categorical data represented by `cat` is one-hot encoded by comparing the results of two methods: using the boolean mask `cat` and using the indices of the categorical features.
    
    Parameters:
    X (array-like): Input array.
    X2 (array-like): Second input array.
    """

    ind = np.where(cat)[0]
    # With mask
    A, B = _run_one_hot(X, X2, cat)
    # With indices
    C, D = _run_one_hot(X, X2, ind)
    # Check shape
    assert_equal(A.shape, (2, n_features))
    assert_equal(B.shape, (1, n_features))
    assert_equal(C.shape, (2, n_features))
    assert_equal(D.shape, (1, n_features))
    # Check that mask and indices give the same results
    assert_array_equal(toarray(A), toarray(C))
    assert_array_equal(toarray(B), toarray(D))


def test_one_hot_encoder_categorical_features():
    """
    Tests the functionality of the OneHotEncoder for different scenarios involving categorical features.
    
    This function evaluates the OneHotEncoder's behavior with various configurations of categorical and non-categorical features. It checks how the encoder handles different combinations of categorical and non-categorical features, including edge cases where all features are either categorical or non-categorical. Additionally, it verifies that an error is raised when attempting to specify both `categories` and `categorical_features`.
    
    Parameters:
    None (The function uses predefined inputs
    """

    X = np.array([[3, 2, 1], [0, 1, 1]])
    X2 = np.array([[1, 1, 1]])

    cat = [True, False, False]
    _check_one_hot(X, X2, cat, 4)

    # Edge case: all non-categorical
    cat = [False, False, False]
    _check_one_hot(X, X2, cat, 3)

    # Edge case: all categorical
    cat = [True, True, True]
    _check_one_hot(X, X2, cat, 5)

    # check error raised if also specifying categories
    oh = OneHotEncoder(categories=[range(3)],
                       categorical_features=[True, False, False])
    assert_raises(ValueError, oh.fit, X)


def test_one_hot_encoder_handle_unknown():
    """
    Summary: This function tests the behavior of the OneHotEncoder class from scikit-learn when handling unknown features.
    
    Important Functions:
    - `OneHotEncoder`: The class being tested, responsible for encoding categorical features as a one-hot numeric array.
    - `fit()`: Fits the OneHotEncoder to the training data.
    - `transform()`: Transforms new data using the fitted OneHotEncoder.
    
    Input Variables:
    - `X`: Training data containing categorical features.
    """

    X = np.array([[0, 2, 1], [1, 0, 3], [1, 0, 2]])
    X2 = np.array([[4, 1, 1]])

    # Test that one hot encoder raises error for unknown features
    # present during transform.
    oh = OneHotEncoder(handle_unknown='error')
    assert_warns(FutureWarning, oh.fit, X)
    assert_raises(ValueError, oh.transform, X2)

    # Test the ignore option, ignores unknown features (giving all 0's)
    oh = OneHotEncoder(handle_unknown='ignore')
    oh.fit(X)
    X2_passed = X2.copy()
    assert_array_equal(
        oh.transform(X2_passed).toarray(),
        np.array([[0.,  0.,  0.,  0.,  1.,  0.,  0.]]))
    # ensure transformed data was not modified in place
    assert_allclose(X2, X2_passed)

    # Raise error if handle_unknown is neither ignore or error.
    oh = OneHotEncoder(handle_unknown='42')
    assert_raises(ValueError, oh.fit, X)


def test_one_hot_encoder_not_fitted():
    """
    Summary: This function tests the behavior of the OneHotEncoder when it has not been fitted.
    
    Keywords: OneHotEncoder, NotFittedError, fit, transform
    
    Input:
    - X (numpy.ndarray): A 2D array containing categorical data to be transformed.
    
    Output:
    - Raises a NotFittedError exception with a specific error message indicating that the OneHotEncoder instance needs to be fitted before calling the transform method.
    """

    X = np.array([['a'], ['b']])
    enc = OneHotEncoder(categories=['a', 'b'])
    msg = ("This OneHotEncoder instance is not fitted yet. "
           "Call 'fit' with appropriate arguments before using this method.")
    with pytest.raises(NotFittedError, match=msg):
        enc.transform(X)


def test_one_hot_encoder_no_categorical_features():
    """
    Tests the behavior of the OneHotEncoder when no categorical features are specified.
    
    This function verifies that the OneHotEncoder correctly handles an input array without any categorical features. It ensures that the transformed output is identical to the input and that no feature names or categories are generated.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `OneHotEncoder`: The class used for encoding non-categorical features.
    - `fit_transform`: Method to fit the encoder to
    """

    X = np.array([[3, 2, 1], [0, 1, 1]], dtype='float64')

    cat = [False, False, False]
    enc = OneHotEncoder(categorical_features=cat)
    with ignore_warnings(category=(DeprecationWarning, FutureWarning)):
        X_tr = enc.fit_transform(X)
    expected_features = np.array(list(), dtype='object')
    assert_array_equal(X, X_tr)
    assert_array_equal(enc.get_feature_names(), expected_features)
    assert enc.categories_ == []


@pytest.mark.parametrize("output_dtype", [np.int32, np.float32, np.float64])
@pytest.mark.parametrize("input_dtype", [np.int32, np.float32, np.float64])
def test_one_hot_encoder_dtype(input_dtype, output_dtype):
    """
    Tests the OneHotEncoder with different data types for input and output.
    
    This function verifies that the `OneHotEncoder` correctly converts a 2D array of integers into a one-hot encoded matrix,
    given specified input and output data types. The function checks both sparse and dense output formats.
    
    Parameters:
    - input_dtype: The data type of the input array (e.g., 'int32', 'float64').
    - output_dtype: The desired data type of the
    """

    X = np.asarray([[0, 1]], dtype=input_dtype).T
    X_expected = np.asarray([[1, 0], [0, 1]], dtype=output_dtype)

    oh = OneHotEncoder(categories='auto', dtype=output_dtype)
    assert_array_equal(oh.fit_transform(X).toarray(), X_expected)
    assert_array_equal(oh.fit(X).transform(X).toarray(), X_expected)

    oh = OneHotEncoder(categories='auto', dtype=output_dtype, sparse=False)
    assert_array_equal(oh.fit_transform(X), X_expected)
    assert_array_equal(oh.fit(X).transform(X), X_expected)


@pytest.mark.parametrize("output_dtype", [np.int32, np.float32, np.float64])
def test_one_hot_encoder_dtype_pandas(output_dtype):
    """
    Tests the OneHotEncoder with specified data types for Pandas DataFrame inputs.
    
    This function evaluates the OneHotEncoder's ability to handle Pandas DataFrame inputs
    and convert them into one-hot encoded arrays with the specified data type. It checks
    both sparse and dense output modes.
    
    Parameters:
    output_dtype (dtype): The desired data type for the output arrays.
    
    Returns:
    None
    
    Functions Used:
    - `pytest.importorskip`: To import the pandas library if
    """

    pd = pytest.importorskip('pandas')

    X_df = pd.DataFrame({'A': ['a', 'b'], 'B': [1, 2]})
    X_expected = np.array([[1, 0, 1, 0], [0, 1, 0, 1]], dtype=output_dtype)

    oh = OneHotEncoder(dtype=output_dtype)
    assert_array_equal(oh.fit_transform(X_df).toarray(), X_expected)
    assert_array_equal(oh.fit(X_df).transform(X_df).toarray(), X_expected)

    oh = OneHotEncoder(dtype=output_dtype, sparse=False)
    assert_array_equal(oh.fit_transform(X_df), X_expected)
    assert_array_equal(oh.fit(X_df).transform(X_df), X_expected)


def test_one_hot_encoder_set_params():
    """
    Set parameters for the OneHotEncoder.
    
    This function sets the categories parameter for the OneHotEncoder and checks if the changes are applied correctly both before and after fitting the encoder to the data. It also verifies that the shape of the transformed data is as expected based on the updated categories.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    AssertionError: If the categories are not correctly set or the shape of the transformed data does not match the expected output.
    
    Example usage
    """

    X = np.array([[1, 2]]).T
    oh = OneHotEncoder()
    # set params on not yet fitted object
    oh.set_params(categories=[[0, 1, 2, 3]])
    assert oh.get_params()['categories'] == [[0, 1, 2, 3]]
    assert oh.fit_transform(X).toarray().shape == (2, 4)
    # set params on already fitted object
    oh.set_params(categories=[[0, 1, 2, 3, 4]])
    assert oh.fit_transform(X).toarray().shape == (2, 5)


def check_categorical_onehot(X):
    """
    Transforms categorical data into one-hot encoded format.
    
    This function takes a dataset `X` containing categorical features and
    converts them into a one-hot encoded format using the `OneHotEncoder`
    from scikit-learn. The transformation is performed twice with slight
    differences: once with a sparse representation and once without. The
    function then asserts that both transformations yield equivalent results
    and returns the dense array form of the sparse matrix obtained from the
    first transformation.
    """

    enc = OneHotEncoder(categories='auto')
    Xtr1 = enc.fit_transform(X)

    enc = OneHotEncoder(categories='auto', sparse=False)
    Xtr2 = enc.fit_transform(X)

    assert_allclose(Xtr1.toarray(), Xtr2)

    assert sparse.isspmatrix_csr(Xtr1)
    return Xtr1.toarray()


@pytest.mark.parametrize("X", [
    [['def', 1, 55], ['abc', 2, 55]],
    np.array([[10, 1, 55], [5, 2, 55]]),
    np.array([['b', 'A', 'cat'], ['a', 'B', 'cat']], dtype=object)
    ], ids=['mixed', 'numeric', 'object'])
def test_one_hot_encoder(X):
    """
    Transforms categorical data into one-hot encoded format.
    
    This function takes a 2D array `X` containing categorical data and
    performs one-hot encoding on the specified columns. The function
    checks the input using `check_categorical_onehot` and then uses
    `OneHotEncoder` from scikit-learn to perform the transformation.
    
    Parameters:
    X (list or numpy.ndarray): A 2D array containing categorical data.
    
    Returns:
    numpy.ndarray: A transformed
    """

    Xtr = check_categorical_onehot(np.array(X)[:, [0]])
    assert_allclose(Xtr, [[0, 1], [1, 0]])

    Xtr = check_categorical_onehot(np.array(X)[:, [0, 1]])
    assert_allclose(Xtr, [[0, 1, 1, 0], [1, 0, 0, 1]])

    Xtr = OneHotEncoder(categories='auto').fit_transform(X)
    assert_allclose(Xtr.toarray(), [[0, 1, 1, 0,  1], [1, 0, 0, 1, 1]])


def test_one_hot_encoder_inverse():
    """
    Tests the inverse_transform method of the OneHotEncoder class.
    
    This function tests the inverse_transform method of the OneHotEncoder class
    for different scenarios. It checks the inverse transformation of both
    categorical and numerical data, handles unknown categories, and ensures
    that the output matches the expected results. The function uses the
    OneHotEncoder from the sklearn.preprocessing module and asserts that the
    transformed and inverse-transformed data are equal.
    
    Parameters:
    None
    
    Returns:
    """

    for sparse_ in [True, False]:
        X = [['abc', 2, 55], ['def', 1, 55], ['abc', 3, 55]]
        enc = OneHotEncoder(sparse=sparse_)
        X_tr = enc.fit_transform(X)
        exp = np.array(X, dtype=object)
        assert_array_equal(enc.inverse_transform(X_tr), exp)

        X = [[2, 55], [1, 55], [3, 55]]
        enc = OneHotEncoder(sparse=sparse_, categories='auto')
        X_tr = enc.fit_transform(X)
        exp = np.array(X)
        assert_array_equal(enc.inverse_transform(X_tr), exp)

        # with unknown categories
        X = [['abc', 2, 55], ['def', 1, 55], ['abc', 3, 55]]
        enc = OneHotEncoder(sparse=sparse_, handle_unknown='ignore',
                            categories=[['abc', 'def'], [1, 2],
                                        [54, 55, 56]])
        X_tr = enc.fit_transform(X)
        exp = np.array(X, dtype=object)
        exp[2, 1] = None
        assert_array_equal(enc.inverse_transform(X_tr), exp)

        # with an otherwise numerical output, still object if unknown
        X = [[2, 55], [1, 55], [3, 55]]
        enc = OneHotEncoder(sparse=sparse_, categories=[[1, 2], [54, 56]],
                            handle_unknown='ignore')
        X_tr = enc.fit_transform(X)
        exp = np.array(X, dtype=object)
        exp[2, 0] = None
        exp[:, 1] = None
        assert_array_equal(enc.inverse_transform(X_tr), exp)

        # incorrect shape raises
        X_tr = np.array([[0, 1, 1], [1, 0, 1]])
        msg = re.escape('Shape of the passed X data is not correct')
        assert_raises_regex(ValueError, msg, enc.inverse_transform, X_tr)


@pytest.mark.parametrize("X, cat_exp, cat_dtype", [
    ([['abc', 55], ['def', 55]], [['abc', 'def'], [55]], np.object_),
    (np.array([[1, 2], [3, 2]]), [[1, 3], [2]], np.integer),
    (np.array([['A', 'cat'], ['B', 'cat']], dtype=object),
     [['A', 'B'], ['cat']], np.object_),
    (np.array([['A', 'cat'], ['B', 'cat']]),
     [['A', 'B'], ['cat']], np.str_)
    ], ids=['mixed', 'numeric', 'object', 'string'])
def test_one_hot_encoder_categories(X, cat_exp, cat_dtype):
    """
    Test the functionality of the OneHotEncoder with specified categories.
    
    This function verifies that the OneHotEncoder correctly identifies and encodes categorical variables,
    regardless of the order of the input samples. It checks that the categories are identified as 'auto',
    returns a list of categories, and ensures that the encoded categories match the expected categories
    and have the correct data type.
    
    Parameters:
    X (array-like): Input data containing categorical variables.
    cat_exp (list of lists): Expected
    """

    # order of categories should not depend on order of samples
    for Xi in [X, X[::-1]]:
        enc = OneHotEncoder(categories='auto')
        enc.fit(Xi)
        # assert enc.categories == 'auto'
        assert isinstance(enc.categories_, list)
        for res, exp in zip(enc.categories_, cat_exp):
            assert res.tolist() == exp
            assert np.issubdtype(res.dtype, cat_dtype)


@pytest.mark.parametrize("X, X2, cats, cat_dtype", [
    (np.array([['a', 'b']], dtype=object).T,
     np.array([['a', 'd']], dtype=object).T,
     [['a', 'b', 'c']], np.object_),
    (np.array([[1, 2]], dtype='int64').T,
     np.array([[1, 4]], dtype='int64').T,
     [[1, 2, 3]], np.int64),
    (np.array([['a', 'b']], dtype=object).T,
     np.array([['a', 'd']], dtype=object).T,
     [np.array(['a', 'b', 'c'])], np.object_),
    ], ids=['object', 'numeric', 'object-string-cat'])
def test_one_hot_encoder_specified_categories(X, X2, cats, cat_dtype):
    """
    This function tests the functionality of the OneHotEncoder class from scikit-learn.
    
    Parameters:
    X (array-like): Input data for fitting the encoder.
    X2 (array-like): Input data for transforming the encoder.
    cats (list of lists): Specified categories for each feature.
    cat_dtype (numpy.dtype): Data type of the categories.
    
    Returns:
    None: This function asserts the correctness of the OneHotEncoder's fit and transform methods.
    
    Important Functions:
    """

    enc = OneHotEncoder(categories=cats)
    exp = np.array([[1., 0., 0.],
                    [0., 1., 0.]])
    assert_array_equal(enc.fit_transform(X).toarray(), exp)
    assert list(enc.categories[0]) == list(cats[0])
    assert enc.categories_[0].tolist() == list(cats[0])
    # manually specified categories should have same dtype as
    # the data when coerced from lists
    assert enc.categories_[0].dtype == cat_dtype

    # when specifying categories manually, unknown categories should already
    # raise when fitting
    enc = OneHotEncoder(categories=cats)
    with pytest.raises(ValueError, match="Found unknown categories"):
        enc.fit(X2)
    enc = OneHotEncoder(categories=cats, handle_unknown='ignore')
    exp = np.array([[1., 0., 0.], [0., 0., 0.]])
    assert_array_equal(enc.fit(X2).transform(X2).toarray(), exp)


def test_one_hot_encoder_unsorted_categories():
    """
    Tests the functionality of the OneHotEncoder for unsorted categories.
    
    This function evaluates the behavior of the OneHotEncoder when the categories
    are specified in an unsorted order. It checks if the encoder correctly handles
    both string and numerical data types, ensuring that the transformed output
    matches the expected one-hot encoded representation.
    
    Parameters:
    None (The function uses predefined input data).
    
    Returns:
    None (The function asserts the correctness of the OneHotEncoder's output).
    """

    X = np.array([['a', 'b']], dtype=object).T

    enc = OneHotEncoder(categories=[['b', 'a', 'c']])
    exp = np.array([[0., 1., 0.],
                    [1., 0., 0.]])
    assert_array_equal(enc.fit(X).transform(X).toarray(), exp)
    assert_array_equal(enc.fit_transform(X).toarray(), exp)
    assert enc.categories_[0].tolist() == ['b', 'a', 'c']
    assert np.issubdtype(enc.categories_[0].dtype, np.object_)

    # unsorted passed categories still raise for numerical values
    X = np.array([[1, 2]]).T
    enc = OneHotEncoder(categories=[[2, 1, 3]])
    msg = 'Unsorted categories are not supported'
    with pytest.raises(ValueError, match=msg):
        enc.fit_transform(X)


def test_one_hot_encoder_specified_categories_mixed_columns():
    """
    Test the functionality of the OneHotEncoder with specified categories for mixed data types.
    
    This function tests the `OneHotEncoder` class from scikit-learn on a dataset containing both categorical (object type) and numerical (integer) columns. The `categories` parameter is explicitly set for each column to ensure that the encoding aligns with the specified categories.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `OneHotEncoder`: Used to encode categorical and
    """

    # multiple columns
    X = np.array([['a', 'b'], [0, 2]], dtype=object).T
    enc = OneHotEncoder(categories=[['a', 'b', 'c'], [0, 1, 2]])
    exp = np.array([[1., 0., 0., 1., 0., 0.],
                    [0., 1., 0., 0., 0., 1.]])
    assert_array_equal(enc.fit_transform(X).toarray(), exp)
    assert enc.categories_[0].tolist() == ['a', 'b', 'c']
    assert np.issubdtype(enc.categories_[0].dtype, np.object_)
    assert enc.categories_[1].tolist() == [0, 1, 2]
    # integer categories but from object dtype data
    assert np.issubdtype(enc.categories_[1].dtype, np.object_)


def test_one_hot_encoder_pandas():
    """
    Tests the `check_categorical_onehot` function using pandas DataFrame.
    
    This function verifies that the `check_categorical_onehot` function correctly
    converts categorical data in a pandas DataFrame into one-hot encoded format.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `pytest.importorskip`: Used to import the pandas library if available.
    - `pd.DataFrame`: Creates a DataFrame from given data.
    - `check_categorical_onehot`: The function being tested
    """

    pd = pytest.importorskip('pandas')

    X_df = pd.DataFrame({'A': ['a', 'b'], 'B': [1, 2]})

    Xtr = check_categorical_onehot(X_df)
    assert_allclose(Xtr, [[1, 0, 1, 0], [0, 1, 0, 1]])


def test_one_hot_encoder_feature_names():
    """
    Generate one-hot encoded feature names from categorical data.
    
    This function takes a list of categorical data and uses the `OneHotEncoder`
    class to transform it into a one-hot encoded format. It then generates
    feature names based on the transformed data.
    
    Parameters:
    None
    
    Returns:
    - feature_names (np.ndarray): Array of generated feature names.
    
    Usage:
    The function can be called without any parameters. It will use a predefined
    dataset `X` to
    """

    enc = OneHotEncoder()
    X = [['Male', 1, 'girl', 2, 3],
         ['Female', 41, 'girl', 1, 10],
         ['Male', 51, 'boy', 12, 3],
         ['Male', 91, 'girl', 21, 30]]

    enc.fit(X)
    feature_names = enc.get_feature_names()
    assert isinstance(feature_names, np.ndarray)

    assert_array_equal(['x0_Female', 'x0_Male',
                        'x1_1', 'x1_41', 'x1_51', 'x1_91',
                        'x2_boy', 'x2_girl',
                        'x3_1', 'x3_2', 'x3_12', 'x3_21',
                        'x4_3',
                        'x4_10', 'x4_30'], feature_names)

    feature_names2 = enc.get_feature_names(['one', 'two',
                                            'three', 'four', 'five'])

    assert_array_equal(['one_Female', 'one_Male',
                        'two_1', 'two_41', 'two_51', 'two_91',
                        'three_boy', 'three_girl',
                        'four_1', 'four_2', 'four_12', 'four_21',
                        'five_3', 'five_10', 'five_30'], feature_names2)

    with pytest.raises(ValueError, match="input_features should have length"):
        enc.get_feature_names(['one', 'two'])


def test_one_hot_encoder_feature_names_unicode():
    """
    Generate one-hot encoded feature names for given input data.
    
    This function uses the `OneHotEncoder` class to transform input data into
    one-hot encoded format and returns the corresponding feature names.
    
    Parameters:
    -----------
    None
    
    Returns:
    --------
    feature_names : list of str
    The generated feature names after one-hot encoding.
    
    Example:
    --------
    >>> enc = OneHotEncoder()
    >>> X = np.array([[u'c❤t1', u
    """

    enc = OneHotEncoder()
    X = np.array([[u'c❤t1', u'dat2']], dtype=object).T
    enc.fit(X)
    feature_names = enc.get_feature_names()
    assert_array_equal([u'x0_c❤t1', u'x0_dat2'], feature_names)
    feature_names = enc.get_feature_names(input_features=[u'n👍me'])
    assert_array_equal([u'n👍me_c❤t1', u'n👍me_dat2'], feature_names)


@pytest.mark.parametrize("X", [np.array([[1, np.nan]]).T,
                               np.array([['a', np.nan]], dtype=object).T],
                         ids=['numeric', 'object'])
@pytest.mark.parametrize("handle_unknown", ['error', 'ignore'])
def test_one_hot_encoder_raise_missing(X, handle_unknown):
    """
    Test the behavior of the OneHotEncoder when handling missing values.
    
    This function evaluates how the `OneHotEncoder` from scikit-learn handles
    missing values (NaNs) based on the specified `handle_unknown` parameter.
    
    Parameters:
    -----------
    X : array-like, shape (n_samples, n_features)
    The input data containing potential missing values (NaNs).
    
    handle_unknown : str
    The strategy to use for unknown categories during transform. Can be
    """

    ohe = OneHotEncoder(categories='auto', handle_unknown=handle_unknown)

    with pytest.raises(ValueError, match="Input contains NaN"):
        ohe.fit(X)

    with pytest.raises(ValueError, match="Input contains NaN"):
        ohe.fit_transform(X)

    ohe.fit(X[:1, :])

    with pytest.raises(ValueError, match="Input contains NaN"):
        ohe.transform(X)


@pytest.mark.parametrize("X", [
    [['abc', 2, 55], ['def', 1, 55]],
    np.array([[10, 2, 55], [20, 1, 55]]),
    np.array([['a', 'B', 'cat'], ['b', 'A', 'cat']], dtype=object)
    ], ids=['mixed', 'numeric', 'object'])
def test_ordinal_encoder(X):
    """
    Encodes categorical features using OrdinalEncoder.
    
    This function takes a 2D array-like object `X` containing categorical
    data and encodes it into numerical form using the `OrdinalEncoder`. The
    encoded output is an array of integers representing the original categories.
    
    Parameters:
    -----------
    X : array-like, shape (n_samples, n_features)
    The input dataset containing categorical data to be encoded.
    
    Returns:
    --------
    transformed_X : numpy.ndarray, shape
    """

    enc = OrdinalEncoder()
    exp = np.array([[0, 1, 0],
                    [1, 0, 0]], dtype='int64')
    assert_array_equal(enc.fit_transform(X), exp.astype('float64'))
    enc = OrdinalEncoder(dtype='int64')
    assert_array_equal(enc.fit_transform(X), exp)


@pytest.mark.parametrize("X, X2, cats, cat_dtype", [
    (np.array([['a', 'b']], dtype=object).T,
     np.array([['a', 'd']], dtype=object).T,
     [['a', 'b', 'c']], np.object_),
    (np.array([[1, 2]], dtype='int64').T,
     np.array([[1, 4]], dtype='int64').T,
     [[1, 2, 3]], np.int64),
    (np.array([['a', 'b']], dtype=object).T,
     np.array([['a', 'd']], dtype=object).T,
     [np.array(['a', 'b', 'c'])], np.object_),
    ], ids=['object', 'numeric', 'object-string-cat'])
def test_ordinal_encoder_specified_categories(X, X2, cats, cat_dtype):
    """
    Encodes categorical features using specified categories.
    
    This function fits an `OrdinalEncoder` to the input data `X` and checks if the transformed output matches the expected result. It also verifies that the categories are correctly set and that manually specified categories have the same dtype as the input data. Additionally, it ensures that unknown categories raise a ValueError during fitting.
    
    Parameters:
    -----------
    X : array-like of shape (n_samples, n_features)
    The input data containing categorical features to be
    """

    enc = OrdinalEncoder(categories=cats)
    exp = np.array([[0.], [1.]])
    assert_array_equal(enc.fit_transform(X), exp)
    assert list(enc.categories[0]) == list(cats[0])
    assert enc.categories_[0].tolist() == list(cats[0])
    # manually specified categories should have same dtype as
    # the data when coerced from lists
    assert enc.categories_[0].dtype == cat_dtype

    # when specifying categories manually, unknown categories should already
    # raise when fitting
    enc = OrdinalEncoder(categories=cats)
    with pytest.raises(ValueError, match="Found unknown categories"):
        enc.fit(X2)


def test_ordinal_encoder_inverse():
    """
    Tests the inverse_transform method of the OrdinalEncoder class.
    
    This function checks if the inverse transformation of the encoded data
    matches the original input data. It also verifies that an error is raised
    when the shape of the transformed data does not match the expected shape.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `OrdinalEncoder`: The class being tested.
    - `fit_transform`: Fits the encoder to the data and transforms it.
    """

    X = [['abc', 2, 55], ['def', 1, 55]]
    enc = OrdinalEncoder()
    X_tr = enc.fit_transform(X)
    exp = np.array(X, dtype=object)
    assert_array_equal(enc.inverse_transform(X_tr), exp)

    # incorrect shape raises
    X_tr = np.array([[0, 1, 1, 2], [1, 0, 1, 0]])
    msg = re.escape('Shape of the passed X data is not correct')
    assert_raises_regex(ValueError, msg, enc.inverse_transform, X_tr)


@pytest.mark.parametrize("X", [np.array([[1, np.nan]]).T,
                               np.array([['a', np.nan]], dtype=object).T],
                         ids=['numeric', 'object'])
def test_ordinal_encoder_raise_missing(X):
    """
    Raises ValueError if the input data contains NaN values when using the OrdinalEncoder.
    
    This function tests the behavior of the OrdinalEncoder from the sklearn.preprocessing module by fitting and transforming various slices of the input data X. It ensures that the encoder raises a ValueError when encountering NaN values in the input data.
    
    Parameters:
    -----------
    X : array-like
    The input data containing features to be encoded.
    
    Returns:
    --------
    None
    
    Raises:
    -------
    ValueError
    """

    ohe = OrdinalEncoder()

    with pytest.raises(ValueError, match="Input contains NaN"):
        ohe.fit(X)

    with pytest.raises(ValueError, match="Input contains NaN"):
        ohe.fit_transform(X)

    ohe.fit(X[:1, :])

    with pytest.raises(ValueError, match="Input contains NaN"):
        ohe.transform(X)


def test_encoder_dtypes():
    """
    Test the preservation of data types during category determination using OneHotEncoder.
    
    This function checks that the data types of the input arrays are preserved
    when determining categories and transforming the data. It tests various
    input types including integer, float, string, and object arrays.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - OneHotEncoder: A scikit-learn preprocessing class for encoding categorical features as a one-hot numeric array.
    - fit:
    """

    # check that dtypes are preserved when determining categories
    enc = OneHotEncoder(categories='auto')
    exp = np.array([[1., 0., 1., 0.], [0., 1., 0., 1.]], dtype='float64')

    for X in [np.array([[1, 2], [3, 4]], dtype='int64'),
              np.array([[1, 2], [3, 4]], dtype='float64'),
              np.array([['a', 'b'], ['c', 'd']]),  # string dtype
              np.array([[1, 'a'], [3, 'b']], dtype='object')]:
        enc.fit(X)
        assert all([enc.categories_[i].dtype == X.dtype for i in range(2)])
        assert_array_equal(enc.transform(X).toarray(), exp)

    X = [[1, 2], [3, 4]]
    enc.fit(X)
    assert all([np.issubdtype(enc.categories_[i].dtype, np.integer)
                for i in range(2)])
    assert_array_equal(enc.transform(X).toarray(), exp)

    X = [[1, 'a'], [3, 'b']]
    enc.fit(X)
    assert all([enc.categories_[i].dtype == 'object' for i in range(2)])
    assert_array_equal(enc.transform(X).toarray(), exp)


def test_encoder_dtypes_pandas():
    """
    Tests the data types handling of the OneHotEncoder for Pandas DataFrames.
    
    This function checks the data types of the encoded output when fitting and transforming
    Pandas DataFrames with the OneHotEncoder. It ensures that the categories are correctly
    identified and encoded based on the input data types.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `pytest.importorskip`: To import the pandas library if available.
    - `OneHotEncoder
    """

    # check dtype (similar to test_categorical_encoder_dtypes for dataframes)
    pd = pytest.importorskip('pandas')

    enc = OneHotEncoder(categories='auto')
    exp = np.array([[1., 0., 1., 0.], [0., 1., 0., 1.]], dtype='float64')

    X = pd.DataFrame({'A': [1, 2], 'B': [3, 4]}, dtype='int64')
    enc.fit(X)
    assert all([enc.categories_[i].dtype == 'int64' for i in range(2)])
    assert_array_equal(enc.transform(X).toarray(), exp)

    X = pd.DataFrame({'A': [1, 2], 'B': ['a', 'b']})
    enc.fit(X)
    assert all([enc.categories_[i].dtype == 'object' for i in range(2)])
    assert_array_equal(enc.transform(X).toarray(), exp)


def test_one_hot_encoder_warning():
    """
    Test the OneHotEncoder class for potential warnings when fitting and transforming input data.
    
    This function checks if there are any warnings generated when using the `fit_transform` method of the OneHotEncoder class from the scikit-learn library. The input data consists of a list of lists containing categorical and numerical values. The function ensures that the OneHotEncoder is correctly handling the input without producing any warnings.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - One
    """

    enc = OneHotEncoder()
    X = [['Male', 1], ['Female', 3]]
    np.testing.assert_no_warnings(enc.fit_transform, X)
