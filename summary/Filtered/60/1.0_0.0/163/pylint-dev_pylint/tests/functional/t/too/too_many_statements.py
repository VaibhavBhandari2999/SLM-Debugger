# pylint: disable=missing-docstring, invalid-name

from __future__ import print_function

def stupid_function(arg): # [too-many-statements]
    if arg == 1:
        print(1)
    elif arg == 2:
        print(1)
    elif arg == 3:
        print(1)
    elif arg == 4:
        print(1)
    elif arg == 5:
        print(1)
    elif arg == 6:
        print(1)
    elif arg == 7:
        print(1)
    elif arg == 8:
        print(1)
    elif arg == 9:
        print(1)
    elif arg == 10:
        print(1)
    elif arg < 1:
        print(1)
        print(1)
        arg = 0
    for _ in range(arg):
        print(1)
        print(1)
        print(1)
        print(1)
        print(1)
        print(1)
        print(1)
        print(1)
        print(1)
        print(1)
        print(1)
        print(1)
        print(1)
        print(1)
        print(1)
        print(1)
        print(1)
        print(1)
        print(1)
        print(1)
        print(1)
        print(1)
        print(1)
        print(1)
        print(1)
        print(1)
        print(1)
        print(1)
        print(1)
        print(1)

def long_function_with_inline_def(fake): # [too-many-statements]
    """
    Generate a function with a long inline definition.
    
    Args:
    fake (int): The initial value to be manipulated by the function.
    
    Returns:
    int: The final value of `fake` after all operations.
    """

    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    def an_inline_function(var):
        return var + var
    fake = an_inline_function(fake)
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1
    fake += 1


def exmaple_function():  # [too-many-statements]
    """
    Generate a Python docstring for the provided function.
    
    This function multiplies two numbers and adds a third number to the result.
    It then prints the final result.
    
    Parameters:
    a (int): The first number to be multiplied.
    b (int): The second number to be multiplied.
    c (int): The number to be added to the product of a and b.
    
    Returns:
    None: This function does not return any value. It only prints the result.
    """

    a = 1
    b = 2
    c = 3
    d = a * b + c
    print(d)
