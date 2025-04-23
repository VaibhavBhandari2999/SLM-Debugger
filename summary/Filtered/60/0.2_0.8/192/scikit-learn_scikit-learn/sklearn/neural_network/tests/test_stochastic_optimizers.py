import numpy as np

from sklearn.neural_network._stochastic_optimizers import (BaseOptimizer,
                                                           SGDOptimizer,
                                                           AdamOptimizer)
from sklearn.utils.testing import (assert_array_equal, assert_equal)


shapes = [(4, 6), (6, 8), (7, 8, 9)]


def test_base_optimizer():
    """
    Function: test_base_optimizer
    
    This function tests the BaseOptimizer class with different learning rates (lr).
    
    Parameters:
    - params (list): A list of numpy arrays representing the parameters of the model.
    
    Returns:
    None: This function does not return any value. It asserts whether the optimizer's trigger_stopping method returns the expected result.
    
    Note:
    - The function iterates over a range of learning rates from 10^-3 to 10^3.
    - For each learning
    """

    params = [np.zeros(shape) for shape in shapes]

    for lr in [10 ** i for i in range(-3, 4)]:
        optimizer = BaseOptimizer(params, lr)
        assert optimizer.trigger_stopping('', False)


def test_sgd_optimizer_no_momentum():
    params = [np.zeros(shape) for shape in shapes]

    for lr in [10 ** i for i in range(-3, 4)]:
        optimizer = SGDOptimizer(params, lr, momentum=0, nesterov=False)
        grads = [np.random.random(shape) for shape in shapes]
        expected = [param - lr * grad for param, grad in zip(params, grads)]
        optimizer.update_params(grads)

        for exp, param in zip(expected, optimizer.params):
            assert_array_equal(exp, param)


def test_sgd_optimizer_momentum():
    """
    Tests the SGD optimizer with momentum.
    
    This function initializes parameters and an optimizer with a specified learning rate and momentum. It then updates the parameters based on random gradients and checks if the updated parameters match the expected values.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Parameters:
    - `shapes`: List of shapes for the parameters.
    - `lr`: Learning rate for the optimizer.
    - `momentum`: Momentum value for the optimizer.
    
    Keywords:
    - `nesterov`: Boolean
    """

    params = [np.zeros(shape) for shape in shapes]
    lr = 0.1

    for momentum in np.arange(0.5, 0.9, 0.1):
        optimizer = SGDOptimizer(params, lr, momentum=momentum, nesterov=False)
        velocities = [np.random.random(shape) for shape in shapes]
        optimizer.velocities = velocities
        grads = [np.random.random(shape) for shape in shapes]
        updates = [momentum * velocity - lr * grad
                   for velocity, grad in zip(velocities, grads)]
        expected = [param + update for param, update in zip(params, updates)]
        optimizer.update_params(grads)

        for exp, param in zip(expected, optimizer.params):
            assert_array_equal(exp, param)


def test_sgd_optimizer_trigger_stopping():
    params = [np.zeros(shape) for shape in shapes]
    lr = 2e-6
    optimizer = SGDOptimizer(params, lr, lr_schedule='adaptive')
    assert not optimizer.trigger_stopping('', False)
    assert_equal(lr / 5, optimizer.learning_rate)
    assert optimizer.trigger_stopping('', False)


def test_sgd_optimizer_nesterovs_momentum():
    params = [np.zeros(shape) for shape in shapes]
    lr = 0.1

    for momentum in np.arange(0.5, 0.9, 0.1):
        optimizer = SGDOptimizer(params, lr, momentum=momentum, nesterov=True)
        velocities = [np.random.random(shape) for shape in shapes]
        optimizer.velocities = velocities
        grads = [np.random.random(shape) for shape in shapes]
        updates = [momentum * velocity - lr * grad
                   for velocity, grad in zip(velocities, grads)]
        updates = [momentum * update - lr * grad
                   for update, grad in zip(updates, grads)]
        expected = [param + update for param, update in zip(params, updates)]
        optimizer.update_params(grads)

        for exp, param in zip(expected, optimizer.params):
            assert_array_equal(exp, param)


def test_adam_optimizer():
    """
    Tests the AdamOptimizer class.
    
    This function tests the AdamOptimizer class by iterating over different values of beta_1 and beta_2, and comparing the computed updates to the expected values.
    
    Parameters:
    None
    
    Returns:
    None
    
    Key Parameters:
    - `lr`: Learning rate for the optimizer.
    - `epsilon`: A small constant for numerical stability.
    - `beta_1`: Exponential decay rate for the first moment estimates.
    - `beta_2`: Exponential decay
    """

    params = [np.zeros(shape) for shape in shapes]
    lr = 0.001
    epsilon = 1e-8

    for beta_1 in np.arange(0.9, 1.0, 0.05):
        for beta_2 in np.arange(0.995, 1.0, 0.001):
            optimizer = AdamOptimizer(params, lr, beta_1, beta_2, epsilon)
            ms = [np.random.random(shape) for shape in shapes]
            vs = [np.random.random(shape) for shape in shapes]
            t = 10
            optimizer.ms = ms
            optimizer.vs = vs
            optimizer.t = t - 1
            grads = [np.random.random(shape) for shape in shapes]

            ms = [beta_1 * m + (1 - beta_1) * grad
                  for m, grad in zip(ms, grads)]
            vs = [beta_2 * v + (1 - beta_2) * (grad ** 2)
                  for v, grad in zip(vs, grads)]
            learning_rate = lr * np.sqrt(1 - beta_2 ** t) / (1 - beta_1**t)
            updates = [-learning_rate * m / (np.sqrt(v) + epsilon)
                       for m, v in zip(ms, vs)]
            expected = [param + update
                        for param, update in zip(params, updates)]

            optimizer.update_params(grads)
            for exp, param in zip(expected, optimizer.params):
                assert_array_equal(exp, param)
