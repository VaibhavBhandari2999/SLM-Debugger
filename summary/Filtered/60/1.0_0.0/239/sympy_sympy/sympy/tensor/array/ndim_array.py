from __future__ import print_function, division
import collections

from sympy import Basic
from sympy.core.compatibility import SYMPY_INTS


class NDimArray(object):
    """

    Examples
    ========

    Create an N-dim array of zeros:

    >>> from sympy import MutableDenseNDimArray
    >>> a = MutableDenseNDimArray.zeros(2, 3, 4)
    >>> a
    [[[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]]

    Create an N-dim array from a list;

    >>> a = MutableDenseNDimArray([[2, 3], [4, 5]])
    >>> a
    [[2, 3], [4, 5]]

    >>> b = MutableDenseNDimArray([[[1, 2], [3, 4], [5, 6]], [[7, 8], [9, 10], [11, 12]]])
    >>> b
    [[[1, 2], [3, 4], [5, 6]], [[7, 8], [9, 10], [11, 12]]]

    Create an N-dim array from a flat list with dimension shape:

    >>> a = MutableDenseNDimArray([1, 2, 3, 4, 5, 6], (2, 3))
    >>> a
    [[1, 2, 3], [4, 5, 6]]

    Create an N-dim array from a matrix:

    >>> from sympy import Matrix
    >>> a = Matrix([[1,2],[3,4]])
    >>> a
    Matrix([
    [1, 2],
    [3, 4]])
    >>> b = MutableDenseNDimArray(a)
    >>> b
    [[1, 2], [3, 4]]

    Arithmetic operations on N-dim arrays

    >>> a = MutableDenseNDimArray([1, 1, 1, 1], (2, 2))
    >>> b = MutableDenseNDimArray([4, 4, 4, 4], (2, 2))
    >>> c = a + b
    >>> c
    [[5, 5], [5, 5]]
    >>> a - b
    [[-3, -3], [-3, -3]]

    """

    _diff_wrt = True

    def __new__(cls, *args, **kwargs):
        from sympy.tensor.array import ImmutableDenseNDimArray
        return ImmutableDenseNDimArray(*args, **kwargs)

    def _parse_index(self, index):
        """
        Parse an index to a unique integer representation.
        
        Parameters:
        index (int or tuple of int): The index or tuple of indices to be parsed. If an integer is provided, it is assumed to be a single index. If a tuple is provided, it represents multi-dimensional indices.
        
        Returns:
        int: The unique integer representation of the index.
        
        Raises:
        ValueError: If the index is out of the valid range or if the length of the index tuple does not match the rank of the array
        """


        if isinstance(index, (SYMPY_INTS, Integer)):
            if index >= self._loop_size:
                raise ValueError("index out of range")
            return index

        if len(index) != self._rank:
            raise ValueError('Wrong number of array axes')

        real_index = 0
        # check if input index can exist in current indexing
        for i in range(self._rank):
            if index[i] >= self.shape[i]:
                raise ValueError('Index ' + str(index) + ' out of border')
            real_index = real_index*self.shape[i] + index[i]

        return real_index

    def _get_tuple_index(self, integer_index):
        """
        Get the tuple index from an integer index.
        
        Args:
        integer_index (int): The integer index to convert to a tuple index.
        
        Returns:
        tuple: The tuple index corresponding to the integer index.
        
        This function takes an integer index and converts it to a tuple index based on the shape of the object. The shape is a list of integers representing the dimensions of the object. The function iterates over the reversed shape, calculating the index for each dimension and then reversing the list to return a tuple
        """

        index = []
        for i, sh in enumerate(reversed(self.shape)):
            index.append(integer_index % sh)
            integer_index //= sh
        index.reverse()
        return tuple(index)

    def _check_symbolic_index(self, index):
        """
        Checks if the provided index is symbolic and processes it accordingly.
        
        Parameters:
        index (int or tuple): The index or tuple of indices to be checked.
        
        Returns:
        Indexed: If the index is symbolic, returns an Indexed object.
        None: If the index is not symbolic.
        
        This function verifies if any part of the provided index is symbolic (i.e., an instance of `Expr` but not a number). If a symbolic index is found, it ensures that the index is within the valid
        """

        # Check if any index is symbolic:
        tuple_index = (index if isinstance(index, tuple) else (index,))
        if any([(isinstance(i, Expr) and (not i.is_number)) for i in tuple_index]):
            for i, nth_dim in zip(tuple_index, self.shape):
                if ((i < 0) == True) or ((i >= nth_dim) == True):
                    raise ValueError("index out of range")
            from sympy.tensor import Indexed
            return Indexed(self, *tuple_index)
        return None

    def _setter_iterable_check(self, value):
        """
        Sets a value if it is not an iterable, MatrixBase, or NDimArray. Raises a NotImplementedError if the value is an iterable, MatrixBase, or NDimArray.
        
        Parameters:
        value: The value to be checked and potentially set.
        
        Returns:
        None
        
        Raises:
        NotImplementedError: If the value is an instance of collections.Iterable, MatrixBase, or NDimArray.
        """

        from sympy.matrices.matrices import MatrixBase
        if isinstance(value, (collections.Iterable, MatrixBase, NDimArray)):
            raise NotImplementedError

    @classmethod
    def _scan_iterable_shape(cls, iterable):
        """
        Determine the shape of an iterable.
        
        This function recursively scans an iterable to determine its shape. It supports nested iterables and returns a tuple representing the shape of the iterable.
        
        Parameters:
        iterable (Iterable): The input iterable whose shape is to be determined.
        
        Returns:
        Tuple[List[Any], Tuple[int, ...]]: A tuple containing a list of elements and a shape tuple. The shape tuple indicates the dimensions of the iterable, starting with the number of dimensions.
        
        Raises:
        ValueError: If
        """

        def f(pointer):
            """
            Determine the flattened structure and shape of a nested iterable.
            
            This function takes a pointer (which can be a nested iterable) and returns a flattened list of all elements along with their original shape. It supports any nested structure of iterables.
            
            Parameters:
            pointer (iterable): The nested iterable to be processed.
            
            Returns:
            tuple: A tuple containing two elements:
            - A list of all elements in the flattened structure.
            - A tuple representing the shape of the original nested structure.
            
            Raises
            """

            if not isinstance(pointer, collections.Iterable):
                return [pointer], ()

            result = []
            elems, shapes = zip(*[f(i) for i in pointer])
            if len(set(shapes)) != 1:
                raise ValueError("could not determine shape unambiguously")
            for i in elems:
                result.extend(i)
            return result, (len(shapes),)+shapes[0]

        return f(iterable)

    @classmethod
    def _handle_ndarray_creation_inputs(cls, iterable=None, shape=None, **kwargs):
        """
        Generate a N-dimensional array from given inputs.
        
        This function handles the creation of a N-dimensional array from various inputs, including iterables, matrices, and other N-dimensional arrays. It ensures that the shape and iterable inputs are correctly interpreted and validated.
        
        Parameters:
        iterable (iterable, optional): An iterable object from which to construct the N-dimensional array.
        shape (tuple, optional): A tuple specifying the shape of the N-dimensional array. If not provided, it will be inferred from the iterable
        """

        from sympy.matrices.matrices import MatrixBase

        if shape is None and iterable is None:
            shape = ()
            iterable = ()
        # Construction from another `NDimArray`:
        elif shape is None and isinstance(iterable, NDimArray):
            shape = iterable.shape
            iterable = list(iterable)
        # Construct N-dim array from an iterable (numpy arrays included):
        elif shape is None and isinstance(iterable, collections.Iterable):
            iterable, shape = cls._scan_iterable_shape(iterable)

        # Construct N-dim array from a Matrix:
        elif shape is None and isinstance(iterable, MatrixBase):
            shape = iterable.shape

        # Construct N-dim array from another N-dim array:
        elif shape is None and isinstance(iterable, NDimArray):
            shape = iterable.shape

        # Construct NDimArray(iterable, shape)
        elif shape is not None:
            pass

        else:
            shape = ()
            iterable = (iterable,)

        if isinstance(shape, (SYMPY_INTS, Integer)):
            shape = (shape,)

        if any([not isinstance(dim, (SYMPY_INTS, Integer)) for dim in shape]):
            raise TypeError("Shape should contain integers only.")

        return tuple(shape), iterable

    def __len__(self):
        """Overload common function len(). Returns number of elements in array.

        Examples
        ========

        >>> from sympy import MutableDenseNDimArray
        >>> a = MutableDenseNDimArray.zeros(3, 3)
        >>> a
        [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        >>> len(a)
        9

        """
        return self._loop_size

    @property
    def shape(self):
        """
        Returns array shape (dimension).

        Examples
        ========

        >>> from sympy import MutableDenseNDimArray
        >>> a = MutableDenseNDimArray.zeros(3, 3)
        >>> a.shape
        (3, 3)

        """
        return self._shape

    def rank(self):
        """
        Returns rank of array.

        Examples
        ========

        >>> from sympy import MutableDenseNDimArray
        >>> a = MutableDenseNDimArray.zeros(3,4,5,6,3)
        >>> a.rank()
        5

        """
        return self._rank

    def diff(self, *args):
        """
        Calculate the derivative of each element in the array.

        Examples
        ========

        >>> from sympy import ImmutableDenseNDimArray
        >>> from sympy.abc import x, y
        >>> M = ImmutableDenseNDimArray([[x, y], [1, x*y]])
        >>> M.diff(x)
        [[1, 0], [0, y]]

        """
        from sympy import Derivative
        return Derivative(self.as_immutable(), *args, evaluate=True)

    def _eval_derivative(self, arg):
        return self.applyfunc(lambda x: x.diff(arg))

    def applyfunc(self, f):
        """Apply a function to each element of the N-dim array.

        Examples
        ========

        >>> from sympy import ImmutableDenseNDimArray
        >>> m = ImmutableDenseNDimArray([i*2+j for i in range(2) for j in range(2)], (2, 2))
        >>> m
        [[0, 1], [2, 3]]
        >>> m.applyfunc(lambda i: 2*i)
        [[0, 2], [4, 6]]
        """
        return type(self)(map(f, self), self.shape)

    def __str__(self):
        """Returns string, allows to use standard functions print() and str().

        Examples
        ========

        >>> from sympy import MutableDenseNDimArray
        >>> a = MutableDenseNDimArray.zeros(2, 2)
        >>> a
        [[0, 0], [0, 0]]

        """
        def f(sh, shape_left, i, j):
            if len(shape_left) == 1:
                return "["+", ".join([str(self[e]) for e in range(i, j)])+"]"

            sh //= shape_left[0]
            return "[" + ", ".join([f(sh, shape_left[1:], i+e*sh, i+(e+1)*sh) for e in range(shape_left[0])]) + "]" # + "\n"*len(shape_left)

        if self.rank() == 0:
            return self[()].__str__()

        return f(self._loop_size, self.shape, 0, self._loop_size)

    def __repr__(self):
        return self.__str__()

    def tolist(self):
        """
        Conveting MutableDenseNDimArray to one-dim list

        Examples
        ========

        >>> from sympy import MutableDenseNDimArray
        >>> a = MutableDenseNDimArray([1, 2, 3, 4], (2, 2))
        >>> a
        [[1, 2], [3, 4]]
        >>> b = a.tolist()
        >>> b
        [[1, 2], [3, 4]]
        """

        def f(sh, shape_left, i, j):
            if len(shape_left) == 1:
                return [self[e] for e in range(i, j)]
            result = []
            sh //= shape_left[0]
            for e in range(shape_left[0]):
                result.append(f(sh, shape_left[1:], i+e*sh, i+(e+1)*sh))
            return result

        return f(self._loop_size, self.shape, 0, self._loop_size)

    def __add__(self, other):
        """
        Add two NDimArray objects element-wise.
        
        Parameters:
        self (NDimArray): The first NDimArray instance.
        other (NDimArray): The second NDimArray instance to be added to the first.
        
        Returns:
        NDimArray: A new NDimArray instance containing the element-wise sum of the two input arrays.
        
        Raises:
        TypeError: If 'other' is not an instance of NDimArray.
        ValueError: If the shapes of the two arrays
        """

        if not isinstance(other, NDimArray):
            raise TypeError(str(other))

        if self.shape != other.shape:
            raise ValueError("array shape mismatch")
        result_list = [i+j for i,j in zip(self, other)]

        return type(self)(result_list, self.shape)

    def __sub__(self, other):
        """
        Subtracts another NDimArray from the current instance.
        
        This method subtracts the elements of another NDimArray from the current instance, element-wise. The shapes of the two arrays must match.
        
        Parameters:
        other (NDimArray): The NDimArray instance to be subtracted from the current instance.
        
        Returns:
        NDimArray: A new NDimArray instance representing the element-wise subtraction result.
        
        Raises:
        TypeError: If 'other' is not an instance of
        """

        if not isinstance(other, NDimArray):
            raise TypeError(str(other))

        if self.shape != other.shape:
            raise ValueError("array shape mismatch")
        result_list = [i-j for i,j in zip(self, other)]

        return type(self)(result_list, self.shape)

    def __mul__(self, other):
        from sympy.matrices.matrices import MatrixBase

        if isinstance(other, (collections.Iterable,NDimArray, MatrixBase)):
            raise ValueError("scalar expected, use tensorproduct(...) for tensorial product")
        other = sympify(other)
        result_list = [i*other for i in self]
        return type(self)(result_list, self.shape)

    def __rmul__(self, other):
        """
        Multiply a matrix by a scalar on the right.
        
        Parameters:
        other (int, float, or sympify-able object): The scalar value to multiply the matrix by.
        
        Returns:
        Matrix: A new matrix where each element is the product of the original element and the scalar.
        
        Raises:
        ValueError: If `other` is an iterable, an instance of `NDimArray`, or a `MatrixBase` object, indicating that a tensorial product is expected instead of a scalar multiplication.
        
        Notes:
        """

        from sympy.matrices.matrices import MatrixBase

        if isinstance(other, (collections.Iterable,NDimArray, MatrixBase)):
            raise ValueError("scalar expected, use tensorproduct(...) for tensorial product")
        other = sympify(other)
        result_list = [other*i for i in self]
        return type(self)(result_list, self.shape)

    def __div__(self, other):
        """
        Divides each element of the matrix by a scalar value.
        
        Parameters:
        other (int, float, or sympy expression): The scalar value by which each element of the matrix will be divided.
        
        Returns:
        Matrix: A new matrix of the same dimensions as the original, with each element divided by the scalar value.
        
        Raises:
        ValueError: If 'other' is not a scalar (i.e., not an int, float, or sympy expression).
        
        Note:
        The original matrix remains
        """

        from sympy.matrices.matrices import MatrixBase

        if isinstance(other, (collections.Iterable,NDimArray, MatrixBase)):
            raise ValueError("scalar expected")
        other = sympify(other)
        result_list = [i/other for i in self]
        return type(self)(result_list, self.shape)

    def __rdiv__(self, other):
        raise NotImplementedError('unsupported operation on NDimArray')

    def __neg__(self):
        result_list = [-i for i in self]
        return type(self)(result_list, self.shape)

    def __eq__(self, other):
        """
        NDimArray instances can be compared to each other.
        Instances equal if they have same shape and data.

        Examples
        ========

        >>> from sympy import MutableDenseNDimArray
        >>> a = MutableDenseNDimArray.zeros(2, 3)
        >>> b = MutableDenseNDimArray.zeros(2, 3)
        >>> a == b
        True
        >>> c = a.reshape(3, 2)
        >>> c == b
        False
        >>> a[0,0] = 1
        >>> b[0,0] = 2
        >>> a == b
        False
        """
        if not isinstance(other, NDimArray):
            return False
        return (self.shape == other.shape) and (list(self) == list(other))

    def __ne__(self, other):
        return not self == other

    __truediv__ = __div__
    __rtruediv__ = __rdiv__

    def _eval_diff(self, *args, **kwargs):
        if kwargs.pop("evaluate", True):
            return self.diff(*args)
        else:
            return Derivative(self, *args, **kwargs)

    def _eval_transpose(self):
        if self.rank() != 2:
            raise ValueError("array rank not 2")
        from .arrayop import permutedims
        return permutedims(self, (1, 0))

    def transpose(self):
        return self._eval_transpose()

    def _eval_conjugate(self):
        return self.func([i.conjugate() for i in self], self.shape)

    def conjugate(self):
        return self._eval_conjugate()

    def _eval_adjoint(self):
        return self.transpose().conjugate()

    def adjoint(self):
        return self._eval_adjoint()


class ImmutableNDimArray(NDimArray, Basic):
    _op_priority = 11.0

    def __hash__(self):
        return Basic.__hash__(self)

    def as_immutable(self):
        return self

    def as_mutable(self):
        raise NotImplementedError("abstract method")


from sympy.core.numbers import Integer
from sympy.core.sympify import sympify
from sympy.core.function import Derivative
from sympy.core.expr import Expr
