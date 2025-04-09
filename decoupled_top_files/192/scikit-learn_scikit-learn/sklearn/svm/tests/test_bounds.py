import numpy as np
from scipy import sparse as sp

import pytest

from sklearn.svm.bounds import l1_min_c
from sklearn.svm import LinearSVC
from sklearn.linear_model.logistic import LogisticRegression

from sklearn.utils.testing import assert_raises
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
    
    This function determines the minimum value of C (regularization strength) for L1 penalty using the `l1_min_c` function. It then fits a classifier with L1 penalty and checks if all coefficients and intercept are zero when C equals this minimum value. If C is slightly increased, the function verifies that at least one coefficient or intercept is non-zero.
    
    Parameters:
    X (array-like
    """

    min_c = l1_min_c(X, y, loss, fit_intercept, intercept_scaling)

    clf = {
        'log': LogisticRegression(penalty='l1', solver='liblinear',
                                  multi_class='ovr'),
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
    Test that an error is raised when the problem is ill-posed.
    
    This function checks if an error is raised when attempting to solve
    a linear classification problem using the L1 penalty with an
    ill-posed dataset. The function takes two inputs: `X`, a 2D array-like
    object representing the feature matrix, and `y`, a 1D array-like object
    representing the target vector. It uses the `l1_min_c` function from the
    """

    X = [[0, 0], [0, 0]]
    y = [0, 1]
    assert_raises(ValueError, l1_min_c, X, y)


def test_unsupported_loss():
    assert_raises(ValueError, l1_min_c, dense_X, Y1, 'l1')
