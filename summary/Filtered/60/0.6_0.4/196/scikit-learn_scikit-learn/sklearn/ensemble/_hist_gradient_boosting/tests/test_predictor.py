import numpy as np
from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import pytest

from sklearn.ensemble._hist_gradient_boosting.binning import _BinMapper
from sklearn.ensemble._hist_gradient_boosting.grower import TreeGrower
from sklearn.ensemble._hist_gradient_boosting.types import G_H_DTYPE


@pytest.mark.parametrize('max_bins', [200, 256])
def test_boston_dataset(max_bins):
    """
    Tests the functionality of the `_BinMapper` and `TreeGrower` classes using the Boston housing dataset.
    
    This function splits the dataset into training and testing sets, applies binning to the features using `_BinMapper`, and then grows a tree using `TreeGrower`. The grown tree is then used to make predictions and the R2 score is calculated for both the training and testing sets.
    
    Parameters:
    - max_bins (int): The maximum number of bins to use for binning the features.
    """

    boston = load_boston()
    X_train, X_test, y_train, y_test = train_test_split(
        boston.data, boston.target, random_state=42)

    mapper = _BinMapper(max_bins=max_bins, random_state=42)
    X_train_binned = mapper.fit_transform(X_train)

    # Init gradients and hessians to that of least squares loss
    gradients = -y_train.astype(G_H_DTYPE)
    hessians = np.ones(1, dtype=G_H_DTYPE)

    min_samples_leaf = 8
    max_leaf_nodes = 31
    grower = TreeGrower(X_train_binned, gradients, hessians,
                        min_samples_leaf=min_samples_leaf,
                        max_leaf_nodes=max_leaf_nodes, max_bins=max_bins,
                        actual_n_bins=mapper.actual_n_bins_)
    grower.grow()

    predictor = grower.make_predictor(bin_thresholds=mapper.bin_thresholds_)

    assert r2_score(y_train, predictor.predict(X_train)) > 0.85
    assert r2_score(y_test, predictor.predict(X_test)) > 0.70
