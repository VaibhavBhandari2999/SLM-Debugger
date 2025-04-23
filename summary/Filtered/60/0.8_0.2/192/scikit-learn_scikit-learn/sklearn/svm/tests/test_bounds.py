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
    # loss='l2' should raise ValueError
    assert_raise_message(ValueError, "loss type not in",
                         l1_min_c, dense_X, Y1, "l2")


def check_l1_min_c(X, y, loss, fit_intercept=True, intercept_scaling=None):
    """
    Check that the minimum C for L1 penalty is working correctly.
    
    This function verifies that the minimum C value for L1 penalty is correctly
    determined and that the corresponding model coefficients and intercept are
    zero when C is set to this minimum value. It also checks that for a slightly
    larger C value, the coefficients and intercept are non-zero.
    
    Parameters:
    X (array-like): The input features.
    y (array-like): The target labels.
    loss (str): The loss
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
    Test for ill-posed input in l1_min_c.
    
    Parameters:
    X (list): A 2D list representing the input data points.
    y (list): A list representing the target values.
    
    Returns:
    ValueError: If the input data is ill-posed, i.e., if the input matrix X is singular or not full rank.
    
    Raises:
    ValueError: If the input matrix X is singular or not full rank, indicating an ill-posed problem for the l1_min_c
    """

    X = [[0, 0], [0, 0]]
    y = [0, 1]
    assert_raises(ValueError, l1_min_c, X, y)


def test_unsupported_loss():
    assert_raises(ValueError, l1_min_c, dense_X, Y1, 'l1')
