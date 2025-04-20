import numpy as np
from scipy import sparse as sp

from sklearn.svm.bounds import l1_min_c
from sklearn.svm import LinearSVC
from sklearn.linear_model.logistic import LogisticRegression

from sklearn.utils.testing import assert_true, assert_raises
from sklearn.utils.testing import assert_raise_message


dense_X = [[-1, 0], [0, 1], [1, 1], [1, 1]]
sparse_X = sp.csr_matrix(dense_X)

Y1 = [0, 1, 1, 1]
Y2 = [2, 1, 0, 0]


def test_l1_min_c():
    """
    Generate a series of test cases for the l1_min_c function.
    
    This function creates a series of test cases to validate the l1_min_c function
    for different loss functions, input types, and intercept settings. Each test
    case is designed to check the behavior of the l1_min_c function under various
    conditions.
    
    Parameters:
    - losses: A list of loss functions to be tested, including 'squared_hinge' and 'log'.
    - Xs: A dictionary containing different
    """

    losses = ['squared_hinge', 'log']
    Xs = {'sparse': sparse_X, 'dense': dense_X}
    Ys = {'two-classes': Y1, 'multi-class': Y2}
    intercepts = {'no-intercept': {'fit_intercept': False},
                  'fit-intercept': {'fit_intercept': True,
                                    'intercept_scaling': 10}}

    for loss in losses:
        for X_label, X in Xs.items():
            for Y_label, Y in Ys.items():
                for intercept_label, intercept_params in intercepts.items():
                    check = lambda: check_l1_min_c(X, Y, loss,
                                                   **intercept_params)
                    check.description = ('Test l1_min_c loss=%r %s %s %s' %
                                         (loss, X_label, Y_label,
                                          intercept_label))
                    yield check

    # loss='l2' should raise ValueError
    assert_raise_message(ValueError, "loss type not in",
                         l1_min_c, dense_X, Y1, "l2")


def check_l1_min_c(X, y, loss, fit_intercept=True, intercept_scaling=None):
    min_c = l1_min_c(X, y, loss, fit_intercept, intercept_scaling)

    clf = {
        'log': LogisticRegression(penalty='l1'),
        'squared_hinge': LinearSVC(loss='squared_hinge',
                                   penalty='l1', dual=False),
    }[loss]

    clf.fit_intercept = fit_intercept
    clf.intercept_scaling = intercept_scaling

    clf.C = min_c
    clf.fit(X, y)
    assert_true((np.asarray(clf.coef_) == 0).all())
    assert_true((np.asarray(clf.intercept_) == 0).all())

    clf.C = min_c * 1.01
    clf.fit(X, y)
    assert_true((np.asarray(clf.coef_) != 0).any() or
                (np.asarray(clf.intercept_) != 0).any())


def test_ill_posed_min_c():
    """
    Test for ill-posed input in l1_min_c function.
    
    Parameters:
    X (list): A 2D list representing the input data points.
    y (list): A list representing the target values.
    
    Raises:
    ValueError: If the input data is ill-posed, i.e., if the data matrix X is singular or not full rank.
    
    Returns:
    None: This function does not return any value. It raises an exception if the input is invalid.
    """

    X = [[0, 0], [0, 0]]
    y = [0, 1]
    assert_raises(ValueError, l1_min_c, X, y)


def test_unsupported_loss():
    assert_raises(ValueError, l1_min_c, dense_X, Y1, 'l1')
