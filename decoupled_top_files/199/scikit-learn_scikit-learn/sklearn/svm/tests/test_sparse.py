import pytest

import numpy as np
from numpy.testing import assert_array_almost_equal, assert_array_equal
from scipy import sparse

from sklearn import datasets, svm, linear_model, base
from sklearn.datasets import make_classification, load_digits, make_blobs
from sklearn.svm.tests import test_svm
from sklearn.exceptions import ConvergenceWarning
from sklearn.utils.extmath import safe_sparse_dot
from sklearn.utils.testing import (assert_warns,
                                   assert_raise_message, ignore_warnings,
                                   skip_if_32bit)


# test sample 1
X = np.array([[-2, -1], [-1, -1], [-1, -2], [1, 1], [1, 2], [2, 1]])
X_sp = sparse.lil_matrix(X)
Y = [1, 1, 1, 2, 2, 2]
T = np.array([[-1, -1], [2, 2], [3, 2]])
true_result = [1, 2, 2]

# test sample 2
X2 = np.array([[0, 0, 0], [1, 1, 1], [2, 0, 0, ],
               [0, 0, 2], [3, 3, 3]])
X2_sp = sparse.dok_matrix(X2)
Y2 = [1, 2, 2, 2, 3]
T2 = np.array([[-1, -1, -1], [1, 1, 1], [2, 2, 2]])
true_result2 = [1, 2, 3]


iris = datasets.load_iris()
# permute
rng = np.random.RandomState(0)
perm = rng.permutation(iris.target.size)
iris.data = iris.data[perm]
iris.target = iris.target[perm]
# sparsify
iris.data = sparse.csr_matrix(iris.data)


def check_svm_model_equal(dense_svm, sparse_svm, X_train, y_train, X_test):
    """
    Check if a dense Support Vector Machine (SVM) model is equivalent to its sparse counterpart.
    
    This function compares the results of fitting a dense SVM model to a sparse SVM model using the same training data. It ensures that both models produce similar support vectors, dual coefficients, and predictions on test data. The function also handles different kernels and raises appropriate errors when using sparse input with models trained on dense data.
    
    Parameters:
    -----------
    dense_svm : sklearn.svm.SVC or sklearn
    """

    dense_svm.fit(X_train.toarray(), y_train)
    if sparse.isspmatrix(X_test):
        X_test_dense = X_test.toarray()
    else:
        X_test_dense = X_test
    sparse_svm.fit(X_train, y_train)
    assert sparse.issparse(sparse_svm.support_vectors_)
    assert sparse.issparse(sparse_svm.dual_coef_)
    assert_array_almost_equal(dense_svm.support_vectors_,
                              sparse_svm.support_vectors_.toarray())
    assert_array_almost_equal(dense_svm.dual_coef_,
                              sparse_svm.dual_coef_.toarray())
    if dense_svm.kernel == "linear":
        assert sparse.issparse(sparse_svm.coef_)
        assert_array_almost_equal(dense_svm.coef_, sparse_svm.coef_.toarray())
    assert_array_almost_equal(dense_svm.support_, sparse_svm.support_)
    assert_array_almost_equal(dense_svm.predict(X_test_dense),
                              sparse_svm.predict(X_test))
    assert_array_almost_equal(dense_svm.decision_function(X_test_dense),
                              sparse_svm.decision_function(X_test))
    assert_array_almost_equal(dense_svm.decision_function(X_test_dense),
                              sparse_svm.decision_function(X_test_dense))
    if isinstance(dense_svm, svm.OneClassSVM):
        msg = "cannot use sparse input in 'OneClassSVM' trained on dense data"
    else:
        assert_array_almost_equal(dense_svm.predict_proba(X_test_dense),
                                  sparse_svm.predict_proba(X_test), 4)
        msg = "cannot use sparse input in 'SVC' trained on dense data"
    if sparse.isspmatrix(X_test):
        assert_raise_message(ValueError, msg, dense_svm.predict, X_test)


@skip_if_32bit
def test_svc():
    """Check that sparse SVC gives the same result as SVC"""
    # many class dataset:
    X_blobs, y_blobs = make_blobs(n_samples=100, centers=10, random_state=0)
    X_blobs = sparse.csr_matrix(X_blobs)

    datasets = [[X_sp, Y, T], [X2_sp, Y2, T2],
                [X_blobs[:80], y_blobs[:80], X_blobs[80:]],
                [iris.data, iris.target, iris.data]]
    kernels = ["linear", "poly", "rbf", "sigmoid"]
    for dataset in datasets:
        for kernel in kernels:
            clf = svm.SVC(gamma=1, kernel=kernel, probability=True,
                          random_state=0, decision_function_shape='ovo')
            sp_clf = svm.SVC(gamma=1, kernel=kernel, probability=True,
                             random_state=0, decision_function_shape='ovo')
            check_svm_model_equal(clf, sp_clf, *dataset)


def test_unsorted_indices():
    """
    Test that the result with sorted and unsorted indices in CSR format is consistent.
    
    This function verifies that fitting an SVM model on a sparse CSR matrix with
    both sorted and unsorted indices yields the same results. The process involves:
    
    1. Loading the digits dataset and splitting it into training and testing sets.
    2. Creating a sparse CSR matrix from the training data.
    3. Fitting a linear SVM model using the dense and sparse representations of the
    training
    """

    # test that the result with sorted and unsorted indices in csr is the same
    # we use a subset of digits as iris, blobs or make_classification didn't
    # show the problem
    X, y = load_digits(return_X_y=True)
    X_test = sparse.csr_matrix(X[50:100])
    X, y = X[:50], y[:50]

    X_sparse = sparse.csr_matrix(X)
    coef_dense = svm.SVC(kernel='linear', probability=True,
                         random_state=0).fit(X, y).coef_
    sparse_svc = svm.SVC(kernel='linear', probability=True,
                         random_state=0).fit(X_sparse, y)
    coef_sorted = sparse_svc.coef_
    # make sure dense and sparse SVM give the same result
    assert_array_almost_equal(coef_dense, coef_sorted.toarray())

    # reverse each row's indices
    def scramble_indices(X):
        """
        Scrambles the indices of a CSR matrix.
        
        This function takes a CSR (Compressed Sparse Row) matrix `X` as input and
        returns a new CSR matrix with the data and indices scrambled in reverse order
        for each row. The function iterates through each row of the matrix, reverses
        the data and indices, and constructs a new CSR matrix with these scrambled
        values.
        
        Parameters:
        X (csr_matrix): A CSR matrix whose indices are to
        """

        new_data = []
        new_indices = []
        for i in range(1, len(X.indptr)):
            row_slice = slice(*X.indptr[i - 1: i + 1])
            new_data.extend(X.data[row_slice][::-1])
            new_indices.extend(X.indices[row_slice][::-1])
        return sparse.csr_matrix((new_data, new_indices, X.indptr),
                                 shape=X.shape)

    X_sparse_unsorted = scramble_indices(X_sparse)
    X_test_unsorted = scramble_indices(X_test)

    assert not X_sparse_unsorted.has_sorted_indices
    assert not X_test_unsorted.has_sorted_indices

    unsorted_svc = svm.SVC(kernel='linear', probability=True,
                           random_state=0).fit(X_sparse_unsorted, y)
    coef_unsorted = unsorted_svc.coef_
    # make sure unsorted indices give same result
    assert_array_almost_equal(coef_unsorted.toarray(), coef_sorted.toarray())
    assert_array_almost_equal(sparse_svc.predict_proba(X_test_unsorted),
                              sparse_svc.predict_proba(X_test))


def test_svc_with_custom_kernel():
    """
    Test SVC with a custom kernel.
    
    This function evaluates the performance of Support Vector Classifier (SVC)
    using both a built-in linear kernel and a custom kernel defined by the `kfunc`
    function. The custom kernel is implemented using `safe_sparse_dot` for dot product
    calculations. The function compares the predictions made by both classifiers on
    the same input data and asserts that they are equal.
    
    Parameters:
    None
    
    Returns:
    None
    """

    def kfunc(x, y):
        return safe_sparse_dot(x, y.T)
    clf_lin = svm.SVC(kernel='linear').fit(X_sp, Y)
    clf_mylin = svm.SVC(kernel=kfunc).fit(X_sp, Y)
    assert_array_equal(clf_lin.predict(X_sp), clf_mylin.predict(X_sp))


def test_svc_iris():
    """
    Test the sparse Support Vector Classifier (SVC) using the Iris dataset.
    
    This function evaluates the performance of the sparse SVC by comparing its
    results with the dense SVC for different kernel types: 'linear', 'poly',
    and 'rbf'. The comparison is made on support vectors, dual coefficients,
    predictions, and coefficients (for linear kernel only).
    
    Parameters:
    None
    
    Returns:
    None
    
    Methods:
    - `svm.SVC`: Initializes and fits both
    """

    # Test the sparse SVC with the iris dataset
    for k in ('linear', 'poly', 'rbf'):
        sp_clf = svm.SVC(kernel=k).fit(iris.data, iris.target)
        clf = svm.SVC(kernel=k).fit(iris.data.toarray(),
                                                   iris.target)

        assert_array_almost_equal(clf.support_vectors_,
                                  sp_clf.support_vectors_.toarray())
        assert_array_almost_equal(clf.dual_coef_, sp_clf.dual_coef_.toarray())
        assert_array_almost_equal(
            clf.predict(iris.data.toarray()), sp_clf.predict(iris.data))
        if k == 'linear':
            assert_array_almost_equal(clf.coef_, sp_clf.coef_.toarray())


def test_sparse_decision_function():
    """
    Tests the decision_function method of an SVM model.
    
    This function checks the decision_function method by comparing its output
    with the expected values for both multi-class and binary classification
    scenarios. It uses the `safe_sparse_dot` function to compute the dot product
    between the input data and the coefficients, and adds the intercept term.
    
    Parameters:
    None (the function uses pre-defined datasets and models).
    
    Returns:
    None (the function asserts the correctness of the decision_function method
    """

    # Test decision_function

    # Sanity check, test that decision_function implemented in python
    # returns the same as the one in libsvm

    # multi class:
    svc = svm.SVC(kernel='linear', C=0.1, decision_function_shape='ovo')
    clf = svc.fit(iris.data, iris.target)

    dec = safe_sparse_dot(iris.data, clf.coef_.T) + clf.intercept_

    assert_array_almost_equal(dec, clf.decision_function(iris.data))

    # binary:
    clf.fit(X, Y)
    dec = np.dot(X, clf.coef_.T) + clf.intercept_
    prediction = clf.predict(X)
    assert_array_almost_equal(dec.ravel(), clf.decision_function(X))
    assert_array_almost_equal(
        prediction,
        clf.classes_[(clf.decision_function(X) > 0).astype(np.int).ravel()])
    expected = np.array([-1., -0.66, -1., 0.66, 1., 1.])
    assert_array_almost_equal(clf.decision_function(X), expected, 2)


def test_error():
    """
    Test error handling for SVM models.
    
    This function tests various error conditions for different SVM models,
    including invalid values for hyperparameters, incorrect label dimensions,
    and fitting the model with valid inputs. It raises ValueError for
    impossible values of hyperparameters and checks if the predict method
    returns the expected results after fitting the model with valid data.
    
    Parameters:
    None
    
    Returns:
    None
    
    Raises:
    ValueError: If the input parameters are invalid or do not meet the
    """

    # Test that it gives proper exception on deficient input
    # impossible value of C
    with pytest.raises(ValueError):
        svm.SVC(C=-1).fit(X, Y)

    # impossible value of nu
    clf = svm.NuSVC(nu=0.0)
    with pytest.raises(ValueError):
        clf.fit(X_sp, Y)

    Y2 = Y[:-1]  # wrong dimensions for labels
    with pytest.raises(ValueError):
        clf.fit(X_sp, Y2)

    clf = svm.SVC()
    clf.fit(X_sp, Y)
    assert_array_equal(clf.predict(T), true_result)


def test_linearsvc():
    """
    Tests the LinearSVC class from scikit-learn.
    
    This function compares the performance of the LinearSVC class when trained
    on dense and sparse input data. It fits the model on both types of inputs,
    ensuring that the intercept is set correctly and that the coefficients and
    intercepts are almost equal between the two models. The function also checks
    if the predictions made by the models on the respective input types are
    consistent.
    
    Parameters:
    None
    """

    # Similar to test_SVC
    clf = svm.LinearSVC(random_state=0).fit(X, Y)
    sp_clf = svm.LinearSVC(random_state=0).fit(X_sp, Y)

    assert sp_clf.fit_intercept

    assert_array_almost_equal(clf.coef_, sp_clf.coef_, decimal=4)
    assert_array_almost_equal(clf.intercept_, sp_clf.intercept_, decimal=4)

    assert_array_almost_equal(clf.predict(X), sp_clf.predict(X_sp))

    clf.fit(X2, Y2)
    sp_clf.fit(X2_sp, Y2)

    assert_array_almost_equal(clf.coef_, sp_clf.coef_, decimal=4)
    assert_array_almost_equal(clf.intercept_, sp_clf.intercept_, decimal=4)


def test_linearsvc_iris():
    """
    Tests the performance of the sparse LinearSVC and dense LinearSVC on the Iris dataset.
    
    This function compares the sparse and dense versions of the LinearSVC model using the Iris dataset. It fits both models and checks if their fit_intercept, coefficients (coef_), intercepts (intercept_), and predictions (predict) are almost equal. Additionally, it verifies the accuracy of the decision_function method and ensures that the models produce the same results after sparsifying their coefficients.
    
    Parameters:
    """

    # Test the sparse LinearSVC with the iris dataset

    sp_clf = svm.LinearSVC(random_state=0).fit(iris.data, iris.target)
    clf = svm.LinearSVC(random_state=0).fit(iris.data.toarray(), iris.target)

    assert clf.fit_intercept == sp_clf.fit_intercept

    assert_array_almost_equal(clf.coef_, sp_clf.coef_, decimal=1)
    assert_array_almost_equal(clf.intercept_, sp_clf.intercept_, decimal=1)
    assert_array_almost_equal(
        clf.predict(iris.data.toarray()), sp_clf.predict(iris.data))

    # check decision_function
    pred = np.argmax(sp_clf.decision_function(iris.data), 1)
    assert_array_almost_equal(pred, clf.predict(iris.data.toarray()))

    # sparsify the coefficients on both models and check that they still
    # produce the same results
    clf.sparsify()
    assert_array_equal(pred, clf.predict(iris.data))
    sp_clf.sparsify()
    assert_array_equal(pred, sp_clf.predict(iris.data))


def test_weight():
    """
    Test class weights for various machine learning models.
    
    This function evaluates the performance of different machine learning models
    with custom class weights on a synthetic dataset generated using `make_classification`.
    The dataset is split into training and testing sets, and each model is trained
    with class weights set to {0: 5}. The function then predicts the labels for the
    test set and checks if the number of correct predictions is at least 11.
    
    Parameters:
    None
    
    Returns
    """

    # Test class weights
    X_, y_ = make_classification(n_samples=200, n_features=100,
                                 weights=[0.833, 0.167], random_state=0)

    X_ = sparse.csr_matrix(X_)
    for clf in (linear_model.LogisticRegression(),
                svm.LinearSVC(random_state=0),
                svm.SVC()):
        clf.set_params(class_weight={0: 5})
        clf.fit(X_[:180], y_[:180])
        y_pred = clf.predict(X_[180:])
        assert np.sum(y_pred == y_[180:]) >= 11


def test_sample_weights():
    """
    Tests the effect of sample weights on the prediction of individual samples using an SVM classifier.
    
    This function fits an SVM classifier with and without custom sample weights to demonstrate how these weights influence the prediction of specific samples.
    
    Parameters:
    None
    
    Returns:
    None
    
    Methods:
    - `svm.SVC()`: Initializes and trains a Support Vector Machine classifier.
    - `fit()`: Trains the classifier on the given training data and labels.
    - `predict()`: Predicts
    """

    # Test weights on individual samples
    clf = svm.SVC()
    clf.fit(X_sp, Y)
    assert_array_equal(clf.predict([X[2]]), [1.])

    sample_weight = [.1] * 3 + [10] * 3
    clf.fit(X_sp, Y, sample_weight=sample_weight)
    assert_array_equal(clf.predict([X[2]]), [2.])


def test_sparse_liblinear_intercept_handling():
    # Test that sparse liblinear honours intercept_scaling param
    test_svm.test_dense_liblinear_intercept_handling(svm.LinearSVC)


@pytest.mark.parametrize("datasets_index", range(4))
@pytest.mark.parametrize("kernel", ["linear", "poly", "rbf", "sigmoid"])
@skip_if_32bit
def test_sparse_oneclasssvm(datasets_index, kernel):
    """
    Test the equivalence of sparse and dense OneClassSVM models.
    
    This function checks whether the sparse OneClassSVM model produces the same results as the dense OneClassSVM model for various datasets. It supports both many-class and binary classification tasks.
    
    Parameters:
    -----------
    datasets_index : int
    Index of the dataset to be used for testing. The available datasets are:
    - [0]: Many-class dataset (blobs).
    - [1]: Binary classification dataset (
    """

    # Check that sparse OneClassSVM gives the same result as dense OneClassSVM
    # many class dataset:
    X_blobs, _ = make_blobs(n_samples=100, centers=10, random_state=0)
    X_blobs = sparse.csr_matrix(X_blobs)
    datasets = [[X_sp, None, T], [X2_sp, None, T2],
                [X_blobs[:80], None, X_blobs[80:]],
                [iris.data, None, iris.data]]
    dataset = datasets[datasets_index]
    clf = svm.OneClassSVM(gamma=1, kernel=kernel)
    sp_clf = svm.OneClassSVM(gamma=1, kernel=kernel)
    check_svm_model_equal(clf, sp_clf, *dataset)


def test_sparse_realdata():
    """
    Test on a subset of the 20newsgroups dataset using sparse matrices.
    This function evaluates the performance of an SVM classifier with a linear kernel on a small subset of the dataset, ensuring that the input data is correctly converted to sparse format and that the weights are properly initialized. The function compares the results obtained from a dense matrix representation (using `X.toarray()`) with those obtained from a sparse matrix representation (using `sparse.coo_matrix(X)`). The key outputs include
    """

    # Test on a subset from the 20newsgroups dataset.
    # This catches some bugs if input is not correctly converted into
    # sparse format or weights are not correctly initialized.

    data = np.array([0.03771744, 0.1003567, 0.01174647, 0.027069])
    indices = np.array([6, 5, 35, 31])
    indptr = np.array(
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
         1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2,
         2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
         2, 2, 2, 2, 2, 2, 2, 2, 2, 4, 4, 4])
    X = sparse.csr_matrix((data, indices, indptr))
    y = np.array(
        [1., 0., 2., 2., 1., 1., 1., 2., 2., 0., 1., 2., 2.,
         0., 2., 0., 3., 0., 3., 0., 1., 1., 3., 2., 3., 2.,
         0., 3., 1., 0., 2., 1., 2., 0., 1., 0., 2., 3., 1.,
         3., 0., 1., 0., 0., 2., 0., 1., 2., 2., 2., 3., 2.,
         0., 3., 2., 1., 2., 3., 2., 2., 0., 1., 0., 1., 2.,
         3., 0., 0., 2., 2., 1., 3., 1., 1., 0., 1., 2., 1.,
         1., 3.])

    clf = svm.SVC(kernel='linear').fit(X.toarray(), y)
    sp_clf = svm.SVC(kernel='linear').fit(sparse.coo_matrix(X), y)

    assert_array_equal(clf.support_vectors_, sp_clf.support_vectors_.toarray())
    assert_array_equal(clf.dual_coef_, sp_clf.dual_coef_.toarray())


def test_sparse_svc_clone_with_callable_kernel():
    """
    Tests the cloning of an SVM classifier with a callable kernel using sparse input data.
    
    This function verifies that the `fit` method is correctly applied to both sparse and dense representations of the input data, ensuring that the cloned model behaves consistently with the original model.
    
    Parameters:
    None
    
    Returns:
    None
    
    Important Functions:
    - `svm.SVC`: Initializes the SVM classifier with a callable kernel.
    - `base.clone`: Clones the initialized SVM classifier.
    - `
    """

    # Test that the "dense_fit" is called even though we use sparse input
    # meaning that everything works fine.
    a = svm.SVC(C=1, kernel=lambda x, y: x * y.T,
                probability=True, random_state=0)
    b = base.clone(a)

    b.fit(X_sp, Y)
    pred = b.predict(X_sp)
    b.predict_proba(X_sp)

    dense_svm = svm.SVC(C=1, kernel=lambda x, y: np.dot(x, y.T),
                        probability=True, random_state=0)
    pred_dense = dense_svm.fit(X, Y).predict(X)
    assert_array_equal(pred_dense, pred)
    # b.decision_function(X_sp)  # XXX : should be supported


def test_timeout():
    """
    Test a Support Vector Machine (SVM) classifier with a custom kernel and check for convergence warning.
    
    This function initializes an SVM classifier with a custom kernel defined by the dot product of input samples. It then fits the model to the provided training data and checks if a ConvergenceWarning is raised during the fitting process.
    
    Parameters:
    None
    
    Returns:
    None
    
    Functions Used:
    - `svm.SVC`: Initializes the SVM classifier with specified parameters.
    - `assert_warn
    """

    sp = svm.SVC(C=1, kernel=lambda x, y: x * y.T,
                 probability=True, random_state=0, max_iter=1)

    assert_warns(ConvergenceWarning, sp.fit, X_sp, Y)


def test_consistent_proba():
    """
    Test the consistency of predicted probabilities across multiple fits.
    
    This function evaluates whether the predicted probabilities from an SVM
    classifier with probability estimates are consistent when fit multiple times
    under the same conditions. The `svm.SVC` class is used with `probability=True`
    to enable probability estimates, and `max_iter=1` to ensure that the model
    converges quickly. The `ignore_warnings` context manager is used to suppress
    convergence warnings. The function compares the predicted probabilities
    """

    a = svm.SVC(probability=True, max_iter=1, random_state=0)
    with ignore_warnings(category=ConvergenceWarning):
        proba_1 = a.fit(X, Y).predict_proba(X)
    a = svm.SVC(probability=True, max_iter=1, random_state=0)
    with ignore_warnings(category=ConvergenceWarning):
        proba_2 = a.fit(X, Y).predict_proba(X)
    assert_array_almost_equal(proba_1, proba_2)
