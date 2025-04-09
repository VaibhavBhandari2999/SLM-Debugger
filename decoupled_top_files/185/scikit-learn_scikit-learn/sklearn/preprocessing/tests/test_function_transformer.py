import numpy as np
from scipy import sparse

from sklearn.preprocessing import FunctionTransformer
from sklearn.utils.testing import (assert_equal, assert_array_equal,
                                   assert_allclose_dense_sparse)
from sklearn.utils.testing import assert_warns_message, assert_no_warnings


def _make_func(args_store, kwargs_store, func=lambda X, *a, **k: X):
    """
    Generates a function that stores arguments and keyword arguments.
    
    Args:
    args_store (list): A list to store positional arguments.
    kwargs_store (dict): A dictionary to store keyword arguments.
    func (callable, optional): The function to be called with the stored arguments. Defaults to a lambda function that returns the first argument.
    
    Returns:
    callable: A function that appends the given arguments and keyword arguments to the respective stores and calls the specified function with them.
    """

    def _func(X, *args, **kwargs):
        """
        _func(X, *args, **kwargs) -> func(X)
        
        This function takes an input `X` and additional positional arguments (`*args`) and keyword arguments (`**kwargs`). It appends `X`, `*args`, and `**kwargs` to the global lists `args_store` and `kwargs_store`, respectively. Then, it calls another function `func(X)` with the input `X`.
        
        Args:
        X: The primary input variable.
        *args: Additional
        """

        args_store.append(X)
        args_store.extend(args)
        kwargs_store.update(kwargs)
        return func(X)

    return _func


def test_delegate_to_func():
    """
    Function to delegate transformation to a custom function.
    
    This function takes an array-like input `X` and optionally an additional
    argument `y`. It uses a custom function `_make_func` to perform the
    transformation. The custom function is responsible for storing the
    positional and keyword arguments passed to it. The transformation is
    verified by comparing the output with the input `X`.
    
    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
    """

    # (args|kwargs)_store will hold the positional and keyword arguments
    # passed to the function inside the FunctionTransformer.
    args_store = []
    kwargs_store = {}
    X = np.arange(10).reshape((5, 2))
    assert_array_equal(
        FunctionTransformer(_make_func(args_store, kwargs_store)).transform(X),
        X, 'transform should have returned X unchanged',
    )

    # The function should only have received X.
    assert_equal(
        args_store,
        [X],
        'Incorrect positional arguments passed to func: {args}'.format(
            args=args_store,
        ),
    )
    assert_equal(
        kwargs_store,
        {},
        'Unexpected keyword arguments passed to func: {args}'.format(
            args=kwargs_store,
        ),
    )

    # reset the argument stores.
    args_store[:] = []  # python2 compatible inplace list clear.
    kwargs_store.clear()
    y = object()
    transformed = assert_warns_message(
        DeprecationWarning, "pass_y is deprecated",
        FunctionTransformer(
            _make_func(args_store, kwargs_store),
            pass_y=True).transform, X, y)

    assert_array_equal(transformed, X,
                       err_msg='transform should have returned X unchanged')

    # The function should have received X and y.
    assert_equal(
        args_store,
        [X, y],
        'Incorrect positional arguments passed to func: {args}'.format(
            args=args_store,
        ),
    )
    assert_equal(
        kwargs_store,
        {},
        'Unexpected keyword arguments passed to func: {args}'.format(
            args=kwargs_store,
        ),
    )


def test_np_log():
    """
    Transforms an array using the natural logarithm.
    
    This function applies the natural logarithm (np.log1p) to each element of the input array `X`. The transformed array is compared against the result of applying `np.log1p` directly to `X` to ensure consistency.
    
    Parameters:
    -----------
    None
    
    Returns:
    --------
    None
    
    Notes:
    ------
    - Input: A 2D NumPy array `X` with shape (5
    """

    X = np.arange(10).reshape((5, 2))

    # Test that the numpy.log example still works.
    assert_array_equal(
        FunctionTransformer(np.log1p).transform(X),
        np.log1p(X),
    )


def test_kw_arg():
    """
    Rounds the elements of a 2D numpy array using the `np.around` function.
    
    Parameters:
    None
    
    Returns:
    None
    
    The function uses the `FunctionTransformer` class from scikit-learn to apply the `np.around` function to a 2D numpy array `X`. The `np.around` function rounds the elements of the array to a specified number of decimal places (3 in this case).
    
    The transformed array is then compared to
    """

    X = np.linspace(0, 1, num=10).reshape((5, 2))

    F = FunctionTransformer(np.around, kw_args=dict(decimals=3))

    # Test that rounding is correct
    assert_array_equal(F.transform(X),
                       np.around(X, decimals=3))


def test_kw_arg_update():
    """
    FunctionTransformer with keyword arguments: This function demonstrates the usage of the FunctionTransformer from scikit-learn to apply a NumPy rounding operation on a 2D array. The transformer is configured to round the elements to a specified number of decimal places using the `np.around` function. The `kw_args` parameter is used to specify the number of decimal places for rounding. The function updates the `decimals` value in `kw_args` to 1 and verifies that the transformed array matches
    """

    X = np.linspace(0, 1, num=10).reshape((5, 2))

    F = FunctionTransformer(np.around, kw_args=dict(decimals=3))

    F.kw_args['decimals'] = 1

    # Test that rounding is correct
    assert_array_equal(F.transform(X), np.around(X, decimals=1))


def test_kw_arg_reset():
    """
    FunctionTransformer with keyword arguments: This function demonstrates the usage of the FunctionTransformer from scikit-learn to apply a NumPy rounding operation on a 2D array. The FunctionTransformer is configured with keyword arguments to specify the number of decimal places for rounding. The function showcases how modifying the keyword arguments affects the transformation result.
    
    Parameters:
    None
    
    Returns:
    None
    
    Usage:
    The function can be used to transform a 2D array by rounding its elements to a specified
    """

    X = np.linspace(0, 1, num=10).reshape((5, 2))

    F = FunctionTransformer(np.around, kw_args=dict(decimals=3))

    F.kw_args = dict(decimals=1)

    # Test that rounding is correct
    assert_array_equal(F.transform(X), np.around(X, decimals=1))


def test_inverse_transform():
    """
    Test the inverse_transform method of the FunctionTransformer.
    
    This function checks if the inverse_transform method of the FunctionTransformer
    works correctly by comparing the transformed and then inversely transformed
    array with the original array after rounding to three decimal places.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `FunctionTransformer`: The transformer object used to apply a function and its inverse.
    - `np.sqrt`: The square root function applied to the input array.
    """

    X = np.array([1, 4, 9, 16]).reshape((2, 2))

    # Test that inverse_transform works correctly
    F = FunctionTransformer(
        func=np.sqrt,
        inverse_func=np.around, inv_kw_args=dict(decimals=3),
    )
    assert_array_equal(
        F.inverse_transform(F.transform(X)),
        np.around(np.sqrt(X), decimals=3),
    )


def test_check_inverse():
    """
    Tests the `FunctionTransformer` class with various input types and checks its inverse functionality.
    
    This function tests the `FunctionTransformer` class by applying different transformations and their inverses on dense and sparse matrices. It verifies whether the provided functions are correctly applied and inverted. The tests include:
    
    - Applying square root and rounding functions on dense and sparse matrices.
    - Ensuring that the inverse transformation works correctly.
    - Verifying that warnings are raised when the inverse functions are not strictly inverse of each
    """

    X_dense = np.array([1, 4, 9, 16], dtype=np.float64).reshape((2, 2))

    X_list = [X_dense,
              sparse.csr_matrix(X_dense),
              sparse.csc_matrix(X_dense)]

    for X in X_list:
        if sparse.issparse(X):
            accept_sparse = True
        else:
            accept_sparse = False
        trans = FunctionTransformer(func=np.sqrt,
                                    inverse_func=np.around,
                                    accept_sparse=accept_sparse,
                                    check_inverse=True)
        assert_warns_message(UserWarning,
                             "The provided functions are not strictly"
                             " inverse of each other. If you are sure you"
                             " want to proceed regardless, set"
                             " 'check_inverse=False'.",
                             trans.fit, X)

        trans = FunctionTransformer(func=np.expm1,
                                    inverse_func=np.log1p,
                                    accept_sparse=accept_sparse,
                                    check_inverse=True)
        Xt = assert_no_warnings(trans.fit_transform, X)
        assert_allclose_dense_sparse(X, trans.inverse_transform(Xt))

    # check that we don't check inverse when one of the func or inverse is not
    # provided.
    trans = FunctionTransformer(func=np.expm1, inverse_func=None,
                                check_inverse=True)
    assert_no_warnings(trans.fit, X_dense)
    trans = FunctionTransformer(func=None, inverse_func=np.expm1,
                                check_inverse=True)
    assert_no_warnings(trans.fit, X_dense)
