import numpy as np
from scipy import sparse as sp

import pytest

from sklearn.svm.bounds import l1_min_c
from sklearn.svm import LinearSVC
from sklearn.linear_model.logistic import LogisticRegression

from sklearn.utils.testing import assert_raise_message


dense_X = [[-1, 0], [0, 1], [1, 1], [1, 1]]
sparse_X = sp.csr_matrix(dense_X)

Y1 = [0, 1, 1, 1]
Y2 = [2, 1, 0, 0]


@pytest.mark.parametrize('loss', ['squared_hinge', 'log'])
@pytest.mark.parametrize('X_label', ['sparse', 'dense'])
@pytest.mark.parametrize('Y_label', ['two-classes', 'multi-class'])
@pytest.mark.parametrize('intercept_label', ['no-intercept', 'fit-intercept'])
def test_l1_min_c(loss, X_label, Y_label, intercept_label):
    """
    Test L1-minimal penalty parameter (C) for given loss function.
    
    This function evaluates the L1-minimal penalty parameter (C) for a specified
    loss function by fitting models with different intercept settings on given
    datasets and labels.
    
    Parameters:
    -----------
    loss : str
    The loss function to be used for fitting the model.
    X_label : str
    Label indicating the type of input data ('sparse' or 'dense').
    Y_label : str
    """

    Xs = {'sparse': sparse_X, 'dense': dense_X}
    Ys = {'two-classes': Y1, 'multi-class': Y2}
    intercepts = {'no-intercept': {'fit_intercept': False},
                  'fit-intercept': {'fit_intercept': True,
                                    'intercept_scaling': 10}}

    X = Xs[X_label]
    Y = Ys[Y_label]
    intercept_params = intercepts[intercept_label]
    check_l1_min_c(X, Y, loss, **intercept_params)


def test_l1_min_c_l2_loss():
    """
    Test the l1_min_c function with different loss types.
    
    This function checks that the `l1_min_c` function raises a ValueError when
    an unsupported loss type ('l2') is specified. It ensures that the function
    correctly handles invalid inputs by validating the loss parameter.
    
    Parameters:
    -----------
    X : array-like
    The input features.
    Y : array-like
    The target values.
    
    Returns:
    --------
    None
    
    Raises:
    -------
    """

    # loss='l2' should raise ValueError
    assert_raise_message(ValueError, "loss type not in",
                         l1_min_c, dense_X, Y1, "l2")


def check_l1_min_c(X, y, loss, fit_intercept=True, intercept_scaling=None):
    """
    Check that the minimum regularization strength (C) for L1 penalty is correctly identified and applied.
    
    This function determines the minimum value of C (regularization strength) for L1 penalty using the `l1_min_c` function. It then fits a classifier with L1 penalty using either LogisticRegression or LinearSVC based on the specified loss function. The function asserts that when C equals the minimum value, all coefficients and intercept are zero. When C is slightly greater than the minimum value, at
    """

    min_c = l1_min_c(X, y, loss, fit_intercept, intercept_scaling)

    clf = {
        'log': LogisticRegression(penalty='l1', solver='liblinear'),
        'squared_hinge': LinearSVC(loss='squared_hinge',
                                   penalty='l1', dual=False),
    }[loss]

    clf.fit_intercept = fit_intercept
    clf.intercept_scaling = intercept_scaling

    clf.C = min_c
    clf.fit(X, y)
    assert (np.asarray(clf.coef_) == 0).all()
    assert (np.asarray(clf.intercept_) == 0).all()

    clf.C = min_c * 1.01
    clf.fit(X, y)
    assert ((np.asarray(clf.coef_) != 0).any() or
            (np.asarray(clf.intercept_) != 0).any())


def test_ill_posed_min_c():
    """
    Test the `l1_min_c` function for handling ill-posed input.
    
    This function checks if the `l1_min_c` function raises a `ValueError`
    when given an ill-posed input matrix `X` and target vector `y`.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    ValueError: If the `l1_min_c` function does not raise a ValueError
    for the given ill-posed input.
    
    Notes:
    -
    """

    X = [[0, 0], [0, 0]]
    y = [0, 1]
    with pytest.raises(ValueError):
        l1_min_c(X, y)


def test_unsupported_loss():
    with pytest.raises(ValueError):
        l1_min_c(dense_X, Y1, 'l1')
