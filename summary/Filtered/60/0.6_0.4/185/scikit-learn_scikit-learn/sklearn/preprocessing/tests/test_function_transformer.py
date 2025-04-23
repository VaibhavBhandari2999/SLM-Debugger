import numpy as np
from scipy import sparse

from sklearn.preprocessing import FunctionTransformer
from sklearn.utils.testing import (assert_equal, assert_array_equal,
                                   assert_allclose_dense_sparse)
from sklearn.utils.testing import assert_warns_message, assert_no_warnings


def _make_func(args_store, kwargs_store, func=lambda X, *a, **k: X):
    def _func(X, *args, **kwargs):
        args_store.append(X)
        args_store.extend(args)
        kwargs_store.update(kwargs)
        return func(X)

    return _func


def test_delegate_to_func():
    """
    Test the delegate-to-function functionality of the FunctionTransformer.
    
    This function tests the `FunctionTransformer` class by verifying that it correctly
    delegates to a provided function. The function being tested is `_make_func`, which
    is expected to store the arguments passed to it. The test checks that the function
    receives the correct arguments and that the transformation process works as expected.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - The `FunctionTransformer` is used to delegate to the
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
    Transforms the input array using the natural logarithm function.
    
    This function applies the natural logarithm (log1p) to each element of the input array. It is designed to work with a 2D numpy array and uses a `FunctionTransformer` to apply the transformation.
    
    Parameters:
    X (numpy.ndarray): A 2D numpy array with shape (5, 2) containing the input data.
    
    Returns:
    numpy.ndarray: A 2D numpy array of the same shape as
    """

    X = np.arange(10).reshape((5, 2))

    # Test that the numpy.log example still works.
    assert_array_equal(
        FunctionTransformer(np.log1p).transform(X),
        np.log1p(X),
    )


def test_kw_arg():
    X = np.linspace(0, 1, num=10).reshape((5, 2))

    F = FunctionTransformer(np.around, kw_args=dict(decimals=3))

    # Test that rounding is correct
    assert_array_equal(F.transform(X),
                       np.around(X, decimals=3))


def test_kw_arg_update():
    X = np.linspace(0, 1, num=10).reshape((5, 2))

    F = FunctionTransformer(np.around, kw_args=dict(decimals=3))

    F.kw_args['decimals'] = 1

    # Test that rounding is correct
    assert_array_equal(F.transform(X), np.around(X, decimals=1))


def test_kw_arg_reset():
    X = np.linspace(0, 1, num=10).reshape((5, 2))

    F = FunctionTransformer(np.around, kw_args=dict(decimals=3))

    F.kw_args = dict(decimals=1)

    # Test that rounding is correct
    assert_array_equal(F.transform(X), np.around(X, decimals=1))


def test_inverse_transform():
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
    Test the check_inverse functionality of the FunctionTransformer.
    
    This function tests the `FunctionTransformer` class with different input types
    and configurations to ensure that the `check_inverse` functionality works as
    expected. The `check_inverse` parameter is used to verify if the provided
    functions are strictly inverse of each other. If the functions are not strictly
    inverse, a warning is issued.
    
    Parameters
    ----------
    X_dense : numpy.ndarray
    A dense 2D array with shape (2, 2)
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
s.fit, X_dense)
