import numpy as np
import scipy.sparse as sp
from scipy import linalg
from itertools import product

from sklearn.utils.testing import assert_true
from sklearn.utils.testing import assert_almost_equal
from sklearn.utils.testing import assert_array_almost_equal
from sklearn.utils.testing import assert_equal
from sklearn.utils.testing import assert_array_equal
from sklearn.utils.testing import assert_greater
from sklearn.utils.testing import assert_raises
from sklearn.utils.testing import assert_raise_message
from sklearn.utils.testing import ignore_warnings
from sklearn.utils.testing import assert_warns

from sklearn import datasets
from sklearn.metrics import mean_squared_error
from sklearn.metrics import make_scorer
from sklearn.metrics import get_scorer

from sklearn.linear_model.base import LinearRegression
from sklearn.linear_model.ridge import ridge_regression
from sklearn.linear_model.ridge import Ridge
from sklearn.linear_model.ridge import _RidgeGCV
from sklearn.linear_model.ridge import RidgeCV
from sklearn.linear_model.ridge import RidgeClassifier
from sklearn.linear_model.ridge import RidgeClassifierCV
from sklearn.linear_model.ridge import _solve_cholesky
from sklearn.linear_model.ridge import _solve_cholesky_kernel
from sklearn.datasets import make_regression

from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import KFold

from sklearn.utils import check_random_state
from sklearn.datasets import make_multilabel_classification

diabetes = datasets.load_diabetes()
X_diabetes, y_diabetes = diabetes.data, diabetes.target
ind = np.arange(X_diabetes.shape[0])
rng = np.random.RandomState(0)
rng.shuffle(ind)
ind = ind[:200]
X_diabetes, y_diabetes = X_diabetes[ind], y_diabetes[ind]

iris = datasets.load_iris()

X_iris = sp.csr_matrix(iris.data)
y_iris = iris.target

DENSE_FILTER = lambda X: X
SPARSE_FILTER = lambda X: sp.csr_matrix(X)


def test_ridge():
    """
    Test Ridge regression convergence using the score.
    
    This function tests the convergence of Ridge regression for different solvers
    using the score as a metric. It generates random data for the tests and fits
    a Ridge regression model with a specified alpha value. The function checks
    that the model's coefficients have the correct shape and that the model's
    score is above a certain threshold. It also tests the model's ability to
    handle different numbers of samples and features.
    
    Parameters:
    None
    
    Returns:
    None
    """

    # Ridge regression convergence test using score
    # TODO: for this test to be robust, we should use a dataset instead
    # of np.random.
    rng = np.random.RandomState(0)
    alpha = 1.0

    for solver in ("svd", "sparse_cg", "cholesky", "lsqr", "sag"):
        # With more samples than features
        n_samples, n_features = 6, 5
        y = rng.randn(n_samples)
        X = rng.randn(n_samples, n_features)

        ridge = Ridge(alpha=alpha, solver=solver)
        ridge.fit(X, y)
        assert_equal(ridge.coef_.shape, (X.shape[1], ))
        assert_greater(ridge.score(X, y), 0.47)

        if solver in ("cholesky", "sag"):
            # Currently the only solvers to support sample_weight.
            ridge.fit(X, y, sample_weight=np.ones(n_samples))
            assert_greater(ridge.score(X, y), 0.47)

        # With more features than samples
        n_samples, n_features = 5, 10
        y = rng.randn(n_samples)
        X = rng.randn(n_samples, n_features)
        ridge = Ridge(alpha=alpha, solver=solver)
        ridge.fit(X, y)
        assert_greater(ridge.score(X, y), .9)

        if solver in ("cholesky", "sag"):
            # Currently the only solvers to support sample_weight.
            ridge.fit(X, y, sample_weight=np.ones(n_samples))
            assert_greater(ridge.score(X, y), 0.9)


def test_primal_dual_relationship():
    y = y_diabetes.reshape(-1, 1)
    coef = _solve_cholesky(X_diabetes, y, alpha=[1e-2])
    K = np.dot(X_diabetes, X_diabetes.T)
    dual_coef = _solve_cholesky_kernel(K, y, alpha=[1e-2])
    coef2 = np.dot(X_diabetes.T, dual_coef).T
    assert_array_almost_equal(coef, coef2)


def test_ridge_singular():
    # test on a singular matrix
    rng = np.random.RandomState(0)
    n_samples, n_features = 6, 6
    y = rng.randn(n_samples // 2)
    y = np.concatenate((y, y))
    X = rng.randn(n_samples // 2, n_features)
    X = np.concatenate((X, X), axis=0)

    ridge = Ridge(alpha=0)
    ridge.fit(X, y)
    assert_greater(ridge.score(X, y), 0.9)


def test_ridge_regression_sample_weights():
    rng = np.random.RandomState(0)

    for solver in ("cholesky", ):
        for n_samples, n_features in ((6, 5), (5, 10)):
            for alpha in (1.0, 1e-2):
                y = rng.randn(n_samples)
                X = rng.randn(n_samples, n_features)
                sample_weight = 1.0 + rng.rand(n_samples)

                coefs = ridge_regression(X, y,
                                         alpha=alpha,
                                         sample_weight=sample_weight,
                                         solver=solver)

                # Sample weight can be implemented via a simple rescaling
                # for the square loss.
                coefs2 = ridge_regression(
                    X * np.sqrt(sample_weight)[:, np.newaxis],
                    y * np.sqrt(sample_weight),
                    alpha=alpha, solver=solver)
                assert_array_almost_equal(coefs, coefs2)


def test_ridge_sample_weights():
    """
    Test Ridge regression with sample weights.
    
    This function tests the Ridge regression model with different sample weights
    using various solvers. It compares the results with the closed-form solution
    of the weighted regularized least squares.
    
    Parameters
    ----------
    n_samples : int
    Number of samples.
    n_features : int
    Number of features.
    
    Returns
    -------
    None
    
    Notes
    -----
    - The function loops over different combinations of alpha (regularization
    strength), intercept (whether to fit an intercept term), and solver
    """

    # TODO: loop over sparse data as well

    rng = np.random.RandomState(0)
    param_grid = product((1.0, 1e-2), (True, False),
                         ('svd', 'cholesky', 'lsqr', 'sparse_cg'))

    for n_samples, n_features in ((6, 5), (5, 10)):

        y = rng.randn(n_samples)
        X = rng.randn(n_samples, n_features)
        sample_weight = 1.0 + rng.rand(n_samples)

        for (alpha, intercept, solver) in param_grid:

            # Ridge with explicit sample_weight
            est = Ridge(alpha=alpha, fit_intercept=intercept, solver=solver)
            est.fit(X, y, sample_weight=sample_weight)
            coefs = est.coef_
            inter = est.intercept_

            # Closed form of the weighted regularized least square
            # theta = (X^T W X + alpha I)^(-1) * X^T W y
            W = np.diag(sample_weight)
            if intercept is False:
                X_aug = X
                I = np.eye(n_features)
            else:
                dummy_column = np.ones(shape=(n_samples, 1))
                X_aug = np.concatenate((dummy_column, X), axis=1)
                I = np.eye(n_features + 1)
                I[0, 0] = 0

            cf_coefs = linalg.solve(X_aug.T.dot(W).dot(X_aug) + alpha * I,
                                    X_aug.T.dot(W).dot(y))

            if intercept is False:
                assert_array_almost_equal(coefs, cf_coefs)
            else:
                assert_array_almost_equal(coefs, cf_coefs[1:])
                assert_almost_equal(inter, cf_coefs[0])


def test_ridge_shapes():
    # Test shape of coef_ and intercept_
    rng = np.random.RandomState(0)
    n_samples, n_features = 5, 10
    X = rng.randn(n_samples, n_features)
    y = rng.randn(n_samples)
    Y1 = y[:, np.newaxis]
    Y = np.c_[y, 1 + y]

    ridge = Ridge()

    ridge.fit(X, y)
    assert_equal(ridge.coef_.shape, (n_features,))
    assert_equal(ridge.intercept_.shape, ())

    ridge.fit(X, Y1)
    assert_equal(ridge.coef_.shape, (1, n_features))
    assert_equal(ridge.intercept_.shape, (1, ))

    ridge.fit(X, Y)
    assert_equal(ridge.coef_.shape, (2, n_features))
    assert_equal(ridge.intercept_.shape, (2, ))


def test_ridge_intercept():
    # Test intercept with multiple targets GH issue #708
    rng = np.random.RandomState(0)
    n_samples, n_features = 5, 10
    X = rng.randn(n_samples, n_features)
    y = rng.randn(n_samples)
    Y = np.c_[y, 1. + y]

    ridge = Ridge()

    ridge.fit(X, y)
    intercept = ridge.intercept_

    ridge.fit(X, Y)
    assert_almost_equal(ridge.intercept_[0], intercept)
    assert_almost_equal(ridge.intercept_[1], intercept + 1.)


def test_toy_ridge_object():
    """
    Test BayesianRegression ridge classifier.
    
    Parameters
    ----------
    X : array-like, shape (n_samples, n_features)
    Training data.
    Y : array-like, shape (n_samples, n_targets)
    Target values.
    reg : Ridge
    Ridge regression object.
    
    Returns
    -------
    None
    
    Notes
    -----
    - The function tests the behavior of the Ridge regression object with
    different input shapes and types.
    - It verifies the prediction output and the shape of the coefficients and
    intercept.
    - The function
    """

    # Test BayesianRegression ridge classifier
    # TODO: test also n_samples > n_features
    X = np.array([[1], [2]])
    Y = np.array([1, 2])
    reg = Ridge(alpha=0.0)
    reg.fit(X, Y)
    X_test = [[1], [2], [3], [4]]
    assert_almost_equal(reg.predict(X_test), [1., 2, 3, 4])

    assert_equal(len(reg.coef_.shape), 1)
    assert_equal(type(reg.intercept_), np.float64)

    Y = np.vstack((Y, Y)).T

    reg.fit(X, Y)
    X_test = [[1], [2], [3], [4]]

    assert_equal(len(reg.coef_.shape), 2)
    assert_equal(type(reg.intercept_), np.ndarray)


def test_ridge_vs_lstsq():
    # On alpha=0., Ridge and OLS yield the same solution.

    rng = np.random.RandomState(0)
    # we need more samples than features
    n_samples, n_features = 5, 4
    y = rng.randn(n_samples)
    X = rng.randn(n_samples, n_features)

    ridge = Ridge(alpha=0., fit_intercept=False)
    ols = LinearRegression(fit_intercept=False)

    ridge.fit(X, y)
    ols.fit(X, y)
    assert_almost_equal(ridge.coef_, ols.coef_)

    ridge.fit(X, y)
    ols.fit(X, y)
    assert_almost_equal(ridge.coef_, ols.coef_)


def test_ridge_individual_penalties():
    # Tests the ridge object using individual penalties

    rng = np.random.RandomState(42)

    n_samples, n_features, n_targets = 20, 10, 5
    X = rng.randn(n_samples, n_features)
    y = rng.randn(n_samples, n_targets)

    penalties = np.arange(n_targets)

    coef_cholesky = np.array([
        Ridge(alpha=alpha, solver="cholesky").fit(X, target).coef_
        for alpha, target in zip(penalties, y.T)])

    coefs_indiv_pen = [
        Ridge(alpha=penalties, solver=solver, tol=1e-8).fit(X, y).coef_
        for solver in ['svd', 'sparse_cg', 'lsqr', 'cholesky', 'sag', 'saga']]
    for coef_indiv_pen in coefs_indiv_pen:
        assert_array_almost_equal(coef_cholesky, coef_indiv_pen)

    # Test error is raised when number of targets and penalties do not match.
    ridge = Ridge(alpha=penalties[:-1])
    assert_raises(ValueError, ridge.fit, X, y)


def _test_ridge_loo(filter_):
    # test that can work with both dense or sparse matrices
    n_samples = X_diabetes.shape[0]

    ret = []

    fit_intercept = filter_ == DENSE_FILTER
    if fit_intercept:
        X_diabetes_ = X_diabetes - X_diabetes.mean(0)
    else:
        X_diabetes_ = X_diabetes
    ridge_gcv = _RidgeGCV(fit_intercept=fit_intercept)
    ridge = Ridge(alpha=1.0, fit_intercept=fit_intercept)

    # because fit_intercept is applied

    # generalized cross-validation (efficient leave-one-out)
    decomp = ridge_gcv._pre_compute(X_diabetes_, y_diabetes, fit_intercept)
    errors, c = ridge_gcv._errors(1.0, y_diabetes, *decomp)
    values, c = ridge_gcv._values(1.0, y_diabetes, *decomp)

    # brute-force leave-one-out: remove one example at a time
    errors2 = []
    values2 = []
    for i in range(n_samples):
        sel = np.arange(n_samples) != i
        X_new = X_diabetes_[sel]
        y_new = y_diabetes[sel]
        ridge.fit(X_new, y_new)
        value = ridge.predict([X_diabetes_[i]])[0]
        error = (y_diabetes[i] - value) ** 2
        errors2.append(error)
        values2.append(value)

    # check that efficient and brute-force LOO give same results
    assert_almost_equal(errors, errors2)
    assert_almost_equal(values, values2)

    # generalized cross-validation (efficient leave-one-out,
    # SVD variation)
    decomp = ridge_gcv._pre_compute_svd(X_diabetes_, y_diabetes, fit_intercept)
    errors3, c = ridge_gcv._errors_svd(ridge.alpha, y_diabetes, *decomp)
    values3, c = ridge_gcv._values_svd(ridge.alpha, y_diabetes, *decomp)

    # check that efficient and SVD efficient LOO give same results
    assert_almost_equal(errors, errors3)
    assert_almost_equal(values, values3)

    # check best alpha
    ridge_gcv.fit(filter_(X_diabetes), y_diabetes)
    alpha_ = ridge_gcv.alpha_
    ret.append(alpha_)

    # check that we get same best alpha with custom loss_func
    f = ignore_warnings
    scoring = make_scorer(mean_squared_error, greater_is_better=False)
    ridge_gcv2 = RidgeCV(fit_intercept=False, scoring=scoring)
    f(ridge_gcv2.fit)(filter_(X_diabetes), y_diabetes)
    assert_equal(ridge_gcv2.alpha_, alpha_)

    # check that we get same best alpha with custom score_func
    func = lambda x, y: -mean_squared_error(x, y)
    scoring = make_scorer(func)
    ridge_gcv3 = RidgeCV(fit_intercept=False, scoring=scoring)
    f(ridge_gcv3.fit)(filter_(X_diabetes), y_diabetes)
    assert_equal(ridge_gcv3.alpha_, alpha_)

    # check that we get same best alpha with a scorer
    scorer = get_scorer('neg_mean_squared_error')
    ridge_gcv4 = RidgeCV(fit_intercept=False, scoring=scorer)
    ridge_gcv4.fit(filter_(X_diabetes), y_diabetes)
    assert_equal(ridge_gcv4.alpha_, alpha_)

    # check that we get same best alpha with sample weights
    ridge_gcv.fit(filter_(X_diabetes), y_diabetes,
                  sample_weight=np.ones(n_samples))
    assert_equal(ridge_gcv.alpha_, alpha_)

    # simulate several responses
    Y = np.vstack((y_diabetes, y_diabetes)).T

    ridge_gcv.fit(filter_(X_diabetes), Y)
    Y_pred = ridge_gcv.predict(filter_(X_diabetes))
    ridge_gcv.fit(filter_(X_diabetes), y_diabetes)
    y_pred = ridge_gcv.predict(filter_(X_diabetes))

    assert_array_almost_equal(np.vstack((y_pred, y_pred)).T,
                              Y_pred, decimal=5)

    return ret


def _test_ridge_cv_normalize(filter_):
    ridge_cv = RidgeCV(normalize=True, cv=3)
    ridge_cv.fit(filter_(10. * X_diabetes), y_diabetes)

    gs = GridSearchCV(Ridge(normalize=True), cv=3,
                      param_grid={'alpha': ridge_cv.alphas})
    gs.fit(filter_(10. * X_diabetes), y_diabetes)
    assert_equal(gs.best_estimator_.alpha, ridge_cv.alpha_)


def _test_ridge_cv(filter_):
    """
    Test RidgeCV with different filters on the diabetes dataset.
    
    Parameters
    ----------
    filter_ : function
    A function that takes a numpy array as input and returns a filtered version of it.
    
    Returns
    -------
    None
    The function performs in-place testing and does not return any value.
    """

    ridge_cv = RidgeCV()
    ridge_cv.fit(filter_(X_diabetes), y_diabetes)
    ridge_cv.predict(filter_(X_diabetes))

    assert_equal(len(ridge_cv.coef_.shape), 1)
    assert_equal(type(ridge_cv.intercept_), np.float64)

    cv = KFold(5)
    ridge_cv.set_params(cv=cv)
    ridge_cv.fit(filter_(X_diabetes), y_diabetes)
    ridge_cv.predict(filter_(X_diabetes))

    assert_equal(len(ridge_cv.coef_.shape), 1)
    assert_equal(type(ridge_cv.intercept_), np.float64)


def _test_ridge_diabetes(filter_):
    ridge = Ridge(fit_intercept=False)
    ridge.fit(filter_(X_diabetes), y_diabetes)
    return np.round(ridge.score(filter_(X_diabetes), y_diabetes), 5)


def _test_multi_ridge_diabetes(filter_):
    """
    Test multi-output ridge regression on diabetes dataset.
    
    Parameters
    ----------
    X_diabetes : array-like, shape (n_samples, n_features)
    Training data.
    y_diabetes : array-like, shape (n_samples,)
    Target values.
    filter_ : callable
    A function to filter the input data.
    
    Returns
    -------
    ridge : Ridge regression model
    Fitted ridge regression model.
    Y_pred : array-like, shape (n_samples, 2)
    Predicted values for the multi-output regression
    """

    # simulate several responses
    Y = np.vstack((y_diabetes, y_diabetes)).T
    n_features = X_diabetes.shape[1]

    ridge = Ridge(fit_intercept=False)
    ridge.fit(filter_(X_diabetes), Y)
    assert_equal(ridge.coef_.shape, (2, n_features))
    Y_pred = ridge.predict(filter_(X_diabetes))
    ridge.fit(filter_(X_diabetes), y_diabetes)
    y_pred = ridge.predict(filter_(X_diabetes))
    assert_array_almost_equal(np.vstack((y_pred, y_pred)).T,
                              Y_pred, decimal=3)


def _test_ridge_classifiers(filter_):
    n_classes = np.unique(y_iris).shape[0]
    n_features = X_iris.shape[1]
    for reg in (RidgeClassifier(), RidgeClassifierCV()):
        reg.fit(filter_(X_iris), y_iris)
        assert_equal(reg.coef_.shape, (n_classes, n_features))
        y_pred = reg.predict(filter_(X_iris))
        assert_greater(np.mean(y_iris == y_pred), .79)

    cv = KFold(5)
    reg = RidgeClassifierCV(cv=cv)
    reg.fit(filter_(X_iris), y_iris)
    y_pred = reg.predict(filter_(X_iris))
    assert_true(np.mean(y_iris == y_pred) >= 0.8)


def _test_tolerance(filter_):
    ridge = Ridge(tol=1e-5, fit_intercept=False)
    ridge.fit(filter_(X_diabetes), y_diabetes)
    score = ridge.score(filter_(X_diabetes), y_diabetes)

    ridge2 = Ridge(tol=1e-3, fit_intercept=False)
    ridge2.fit(filter_(X_diabetes), y_diabetes)
    score2 = ridge2.score(filter_(X_diabetes), y_diabetes)

    assert_true(score >= score2)


def check_dense_sparse(test_func):
    # test dense matrix
    ret_dense = test_func(DENSE_FILTER)
    # test sparse matrix
    ret_sparse = test_func(SPARSE_FILTER)
    # test that the outputs are the same
    if ret_dense is not None and ret_sparse is not None:
        assert_array_almost_equal(ret_dense, ret_sparse, decimal=3)


def test_dense_sparse():
    for test_func in (_test_ridge_loo,
                      _test_ridge_cv,
                      _test_ridge_cv_normalize,
                      _test_ridge_diabetes,
                      _test_multi_ridge_diabetes,
                      _test_ridge_classifiers,
                      _test_tolerance):
        yield check_dense_sparse, test_func


def test_ridge_cv_sparse_svd():
    """
    Test RidgeCV with sparse input and SVD mode.
    
    Parameters:
    X (scipy.sparse.csr_matrix): Input data in sparse CSR format.
    ridge (RidgeCV): Ridge regression model with cross-validation.
    
    Raises:
    TypeError: If the input data is not in the correct format.
    
    This function tests the RidgeCV model with sparse input data and SVD mode. It expects the input data to be in CSR sparse format. If the input data is not in the correct format, a
    """

    X = sp.csr_matrix(X_diabetes)
    ridge = RidgeCV(gcv_mode="svd")
    assert_raises(TypeError, ridge.fit, X)


def test_ridge_sparse_svd():
    X = sp.csc_matrix(rng.rand(100, 10))
    y = rng.rand(100)
    ridge = Ridge(solver='svd', fit_intercept=False)
    assert_raises(TypeError, ridge.fit, X, y)


def test_class_weights():
    # Test class weights.
    X = np.array([[-1.0, -1.0], [-1.0, 0], [-.8, -1.0],
                  [1.0, 1.0], [1.0, 0.0]])
    y = [1, 1, 1, -1, -1]

    reg = RidgeClassifier(class_weight=None)
    reg.fit(X, y)
    assert_array_equal(reg.predict([[0.2, -1.0]]), np.array([1]))

    # we give a small weights to class 1
    reg = RidgeClassifier(class_weight={1: 0.001})
    reg.fit(X, y)

    # now the hyperplane should rotate clock-wise and
    # the prediction on this point should shift
    assert_array_equal(reg.predict([[0.2, -1.0]]), np.array([-1]))

    # check if class_weight = 'balanced' can handle negative labels.
    reg = RidgeClassifier(class_weight='balanced')
    reg.fit(X, y)
    assert_array_equal(reg.predict([[0.2, -1.0]]), np.array([1]))

    # class_weight = 'balanced', and class_weight = None should return
    # same values when y has equal number of all labels
    X = np.array([[-1.0, -1.0], [-1.0, 0], [-.8, -1.0], [1.0, 1.0]])
    y = [1, 1, -1, -1]
    reg = RidgeClassifier(class_weight=None)
    reg.fit(X, y)
    rega = RidgeClassifier(class_weight='balanced')
    rega.fit(X, y)
    assert_equal(len(rega.classes_), 2)
    assert_array_almost_equal(reg.coef_, rega.coef_)
    assert_array_almost_equal(reg.intercept_, rega.intercept_)


def test_class_weight_vs_sample_weight():
    """Check class_weights resemble sample_weights behavior."""
    for reg in (RidgeClassifier, RidgeClassifierCV):

        # Iris is balanced, so no effect expected for using 'balanced' weights
        reg1 = reg()
        reg1.fit(iris.data, iris.target)
        reg2 = reg(class_weight='balanced')
        reg2.fit(iris.data, iris.target)
        assert_almost_equal(reg1.coef_, reg2.coef_)

        # Inflate importance of class 1, check against user-defined weights
        sample_weight = np.ones(iris.target.shape)
        sample_weight[iris.target == 1] *= 100
        class_weight = {0: 1., 1: 100., 2: 1.}
        reg1 = reg()
        reg1.fit(iris.data, iris.target, sample_weight)
        reg2 = reg(class_weight=class_weight)
        reg2.fit(iris.data, iris.target)
        assert_almost_equal(reg1.coef_, reg2.coef_)

        # Check that sample_weight and class_weight are multiplicative
        reg1 = reg()
        reg1.fit(iris.data, iris.target, sample_weight ** 2)
        reg2 = reg(class_weight=class_weight)
        reg2.fit(iris.data, iris.target, sample_weight)
        assert_almost_equal(reg1.coef_, reg2.coef_)


def test_class_weights_cv():
    """
    Tests the functionality of RidgeClassifierCV with class weights.
    
    This function evaluates the performance of the RidgeClassifierCV with and without custom class weights. It fits the classifier to a predefined dataset and then applies a custom class weight to see how it affects the prediction.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Points:
    - The function uses a predefined dataset with features `X` and labels `y`.
    - It first fits a RidgeClassifierCV without any class weights.
    - Then,
    """

    # Test class weights for cross validated ridge classifier.
    X = np.array([[-1.0, -1.0], [-1.0, 0], [-.8, -1.0],
                  [1.0, 1.0], [1.0, 0.0]])
    y = [1, 1, 1, -1, -1]

    reg = RidgeClassifierCV(class_weight=None, alphas=[.01, .1, 1])
    reg.fit(X, y)

    # we give a small weights to class 1
    reg = RidgeClassifierCV(class_weight={1: 0.001}, alphas=[.01, .1, 1, 10])
    reg.fit(X, y)

    assert_array_equal(reg.predict([[-.2, 2]]), np.array([-1]))


def test_ridgecv_store_cv_values():
    # Test _RidgeCV's store_cv_values attribute.
    rng = rng = np.random.RandomState(42)

    n_samples = 8
    n_features = 5
    x = rng.randn(n_samples, n_features)
    alphas = [1e-1, 1e0, 1e1]
    n_alphas = len(alphas)

    r = RidgeCV(alphas=alphas, store_cv_values=True)

    # with len(y.shape) == 1
    y = rng.randn(n_samples)
    r.fit(x, y)
    assert_equal(r.cv_values_.shape, (n_samples, n_alphas))

    # with len(y.shape) == 2
    n_responses = 3
    y = rng.randn(n_samples, n_responses)
    r.fit(x, y)
    assert_equal(r.cv_values_.shape, (n_samples, n_responses, n_alphas))


def test_ridgecv_sample_weight():
    rng = np.random.RandomState(0)
    alphas = (0.1, 1.0, 10.0)

    # There are different algorithms for n_samples > n_features
    # and the opposite, so test them both.
    for n_samples, n_features in ((6, 5), (5, 10)):
        y = rng.randn(n_samples)
        X = rng.randn(n_samples, n_features)
        sample_weight = 1.0 + rng.rand(n_samples)

        cv = KFold(5)
        ridgecv = RidgeCV(alphas=alphas, cv=cv)
        ridgecv.fit(X, y, sample_weight=sample_weight)

        # Check using GridSearchCV directly
        parameters = {'alpha': alphas}
        gs = GridSearchCV(Ridge(), parameters, cv=cv)
        gs.fit(X, y, sample_weight=sample_weight)

        assert_equal(ridgecv.alpha_, gs.best_estimator_.alpha)
        assert_array_almost_equal(ridgecv.coef_, gs.best_estimator_.coef_)


def test_raises_value_error_if_sample_weights_greater_than_1d():
    """
    Test that a ValueError is raised if sample weights are greater than 1D.
    
    This function checks that the `Ridge` model from scikit-learn raises a
    `ValueError` when sample weights are provided as a 2D array. The function
    iterates over different sample sizes and feature dimensions, generating random
    data and sample weights. It then attempts to fit a Ridge regression model with
    both valid and invalid sample weights to ensure that the ValueError is raised
    for invalid weights.
    """

    # Sample weights must be either scalar or 1D

    n_sampless = [2, 3]
    n_featuress = [3, 2]

    rng = np.random.RandomState(42)

    for n_samples, n_features in zip(n_sampless, n_featuress):
        X = rng.randn(n_samples, n_features)
        y = rng.randn(n_samples)
        sample_weights_OK = rng.randn(n_samples) ** 2 + 1
        sample_weights_OK_1 = 1.
        sample_weights_OK_2 = 2.
        sample_weights_not_OK = sample_weights_OK[:, np.newaxis]
        sample_weights_not_OK_2 = sample_weights_OK[np.newaxis, :]

        ridge = Ridge(alpha=1)

        # make sure the "OK" sample weights actually work
        ridge.fit(X, y, sample_weights_OK)
        ridge.fit(X, y, sample_weights_OK_1)
        ridge.fit(X, y, sample_weights_OK_2)

        def fit_ridge_not_ok():
            ridge.fit(X, y, sample_weights_not_OK)

        def fit_ridge_not_ok_2():
            ridge.fit(X, y, sample_weights_not_OK_2)

        assert_raise_message(ValueError,
                             "Sample weights must be 1D array or scalar",
                             fit_ridge_not_ok)

        assert_raise_message(ValueError,
                             "Sample weights must be 1D array or scalar",
                             fit_ridge_not_ok_2)


def test_sparse_design_with_sample_weights():
    # Sample weights must work with sparse matrices

    n_sampless = [2, 3]
    n_featuress = [3, 2]

    rng = np.random.RandomState(42)

    sparse_matrix_converters = [sp.coo_matrix,
                                sp.csr_matrix,
                                sp.csc_matrix,
                                sp.lil_matrix,
                                sp.dok_matrix
                                ]

    sparse_ridge = Ridge(alpha=1., fit_intercept=False)
    dense_ridge = Ridge(alpha=1., fit_intercept=False)

    for n_samples, n_features in zip(n_sampless, n_featuress):
        X = rng.randn(n_samples, n_features)
        y = rng.randn(n_samples)
        sample_weights = rng.randn(n_samples) ** 2 + 1
        for sparse_converter in sparse_matrix_converters:
            X_sparse = sparse_converter(X)
            sparse_ridge.fit(X_sparse, y, sample_weight=sample_weights)
            dense_ridge.fit(X, y, sample_weight=sample_weights)

            assert_array_almost_equal(sparse_ridge.coef_, dense_ridge.coef_,
                                      decimal=6)


def test_raises_value_error_if_solver_not_supported():
    # Tests whether a ValueError is raised if a non-identified solver
    # is passed to ridge_regression

    wrong_solver = "This is not a solver (MagritteSolveCV QuantumBitcoin)"

    exception = ValueError
    message = "Solver %s not understood" % wrong_solver

    def func():
        """
        Function to perform ridge regression on a given dataset.
        
        Parameters:
        X (numpy.ndarray): Input data matrix of shape (n_samples, n_features).
        y (numpy.ndarray): Target values of shape (n_samples,).
        alpha (float): Regularization strength; must be a positive float.
        solver (str): The solver to use for the ridge regression. Must be one of 'wrong_solver' for demonstration purposes.
        
        Returns:
        numpy.ndarray: The coefficients of the regression model.
        
        Raises
        """

        X = np.eye(3)
        y = np.ones(3)
        ridge_regression(X, y, alpha=1., solver=wrong_solver)

    assert_raise_message(exception, message, func)


def test_sparse_cg_max_iter():
    reg = Ridge(solver="sparse_cg", max_iter=1)
    reg.fit(X_diabetes, y_diabetes)
    assert_equal(reg.coef_.shape[0], X_diabetes.shape[1])


@ignore_warnings
def test_n_iter():
    # Test that self.n_iter_ is correct.
    n_targets = 2
    X, y = X_diabetes, y_diabetes
    y_n = np.tile(y, (n_targets, 1)).T

    for max_iter in range(1, 4):
        for solver in ('sag', 'saga', 'lsqr'):
            reg = Ridge(solver=solver, max_iter=max_iter, tol=1e-12)
            reg.fit(X, y_n)
            assert_array_equal(reg.n_iter_, np.tile(max_iter, n_targets))

    for solver in ('sparse_cg', 'svd', 'cholesky'):
        reg = Ridge(solver=solver, max_iter=1, tol=1e-1)
        reg.fit(X, y_n)
        assert_equal(reg.n_iter_, None)


def test_ridge_fit_intercept_sparse():
    """
    Test Ridge regression with fit_intercept=True on sparse input.
    
    This function checks the Ridge regression implementation for both dense and
    sparse input when fit_intercept is set to True. It ensures that the
    intercept and coefficients are consistent between dense and sparse input for
    the 'saga' and 'sag' solvers. It also tests the behavior when using the 'lsqr'
    solver, which is not supported and should raise a UserWarning.
    
    Parameters:
    None
    
    Returns:
    None
    """

    X, y = make_regression(n_samples=1000, n_features=2, n_informative=2,
                           bias=10., random_state=42)
    X_csr = sp.csr_matrix(X)

    for solver in ['saga', 'sag']:
        dense = Ridge(alpha=1., tol=1.e-15, solver=solver, fit_intercept=True)
        sparse = Ridge(alpha=1., tol=1.e-15, solver=solver, fit_intercept=True)
        dense.fit(X, y)
        sparse.fit(X_csr, y)
        assert_almost_equal(dense.intercept_, sparse.intercept_)
        assert_array_almost_equal(dense.coef_, sparse.coef_)

    # test the solver switch and the corresponding warning
    sparse = Ridge(alpha=1., tol=1.e-15, solver='lsqr', fit_intercept=True)
    assert_warns(UserWarning, sparse.fit, X_csr, y)
    assert_almost_equal(dense.intercept_, sparse.intercept_)
    assert_array_almost_equal(dense.coef_, sparse.coef_)


def test_errors_and_values_helper():
    """
    Helper function for Ridge regression Generalized Cross Validation (GCV).
    
    This function computes the errors and values used in the GCV calculation for Ridge regression.
    
    Parameters
    ----------
    ridgecv : RidgeCV object
    The RidgeCV object containing the necessary attributes and methods.
    alpha : float
    The regularization strength.
    y : array-like, shape (n_samples,)
    The target values.
    v : array-like, shape (n_samples,)
    The vector used in the GCV calculation.
    Q : array-like
    """

    ridgecv = _RidgeGCV()
    rng = check_random_state(42)
    alpha = 1.
    n = 5
    y = rng.randn(n)
    v = rng.randn(n)
    Q = rng.randn(len(v), len(v))
    QT_y = Q.T.dot(y)
    G_diag, c = ridgecv._errors_and_values_helper(alpha, y, v, Q, QT_y)

    # test that helper function behaves as expected
    out, c_ = ridgecv._errors(alpha, y, v, Q, QT_y)
    np.testing.assert_array_equal(out, (c / G_diag) ** 2)
    np.testing.assert_array_equal(c, c)

    out, c_ = ridgecv._values(alpha, y, v, Q, QT_y)
    np.testing.assert_array_equal(out, y - (c / G_diag))
    np.testing.assert_array_equal(c_, c)


def test_errors_and_values_svd_helper():
    ridgecv = _RidgeGCV()
    rng = check_random_state(42)
    alpha = 1.
    for n, p in zip((5, 10), (12, 6)):
        y = rng.randn(n)
        v = rng.randn(p)
        U = rng.randn(n, p)
        UT_y = U.T.dot(y)
        G_diag, c = ridgecv._errors_and_values_svd_helper(alpha, y, v, U, UT_y)

        # test that helper function behaves as expected
        out, c_ = ridgecv._errors_svd(alpha, y, v, U, UT_y)
        np.testing.assert_array_equal(out, (c / G_diag) ** 2)
        np.testing.assert_array_equal(c, c)

        out, c_ = ridgecv._values_svd(alpha, y, v, U, UT_y)
        np.testing.assert_array_equal(out, y - (c / G_diag))
        np.testing.assert_array_equal(c_, c)


def test_ridge_classifier_no_support_multilabel():
    X, y = make_multilabel_classification(n_samples=10, random_state=0)
    assert_raises(ValueError, RidgeClassifier().fit, X, y)


def test_dtype_match():
    rng = np.random.RandomState(0)
    alpha = 1.0

    n_samples, n_features = 6, 5
    X_64 = rng.randn(n_samples, n_features)
    y_64 = rng.randn(n_samples)
    X_32 = X_64.astype(np.float32)
    y_32 = y_64.astype(np.float32)

    solvers = ["svd", "sparse_cg", "cholesky", "lsqr"]
    for solver in solvers:

        # Check type consistency 32bits
        ridge_32 = Ridge(alpha=alpha, solver=solver)
        ridge_32.fit(X_32, y_32)
        coef_32 = ridge_32.coef_

        # Check type consistency 64 bits
        ridge_64 = Ridge(alpha=alpha, solver=solver)
        ridge_64.fit(X_64, y_64)
        coef_64 = ridge_64.coef_

        # Do the actual checks at once for easier debug
        assert coef_32.dtype == X_32.dtype
        assert coef_64.dtype == X_64.dtype
        assert ridge_32.predict(X_32).dtype == X_32.dtype
        assert ridge_64.predict(X_64).dtype == X_64.dtype
        assert_almost_equal(ridge_32.coef_, ridge_64.coef_, decimal=5)


def test_dtype_match_cholesky():
    # Test different alphas in cholesky solver to ensure full coverage.
    # This test is separated from test_dtype_match for clarity.
    rng = np.random.RandomState(0)
    alpha = (1.0, 0.5)

    n_samples, n_features, n_target = 6, 7, 2
    X_64 = rng.randn(n_samples, n_features)
    y_64 = rng.randn(n_samples, n_target)
    X_32 = X_64.astype(np.float32)
    y_32 = y_64.astype(np.float32)

    # Check type consistency 32bits
    ridge_32 = Ridge(alpha=alpha, solver='cholesky')
    ridge_32.fit(X_32, y_32)
    coef_32 = ridge_32.coef_

    # Check type consistency 64 bits
    ridge_64 = Ridge(alpha=alpha, solver='cholesky')
    ridge_64.fit(X_64, y_64)
    coef_64 = ridge_64.coef_

    # Do all the checks at once, like this is easier to debug
    assert coef_32.dtype == X_32.dtype
    assert coef_64.dtype == X_64.dtype
    assert ridge_32.predict(X_32).dtype == X_32.dtype
    assert ridge_64.predict(X_64).dtype == X_64.dtype
    assert_almost_equal(ridge_32.coef_, ridge_64.coef_, decimal=5)
