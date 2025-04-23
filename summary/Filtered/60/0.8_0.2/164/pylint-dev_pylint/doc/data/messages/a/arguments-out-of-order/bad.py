def function_3_args(first_argument, second_argument, third_argument):
    """Three arguments function"""
    return first_argument, second_argument, third_argument


def args_out_of_order():
    """
    This function takes three arguments: first_argument, second_argument, and third_argument. It processes these arguments in a specific order and returns a result.
    
    Args:
    first_argument (int): The first integer argument.
    second_argument (int): The second integer argument.
    third_argument (int): The third integer argument.
    
    Returns:
    int: The processed result of the three arguments.
    """

    first_argument = 1
    second_argument = 2
    third_argument = 3

    function_3_args(  # [arguments-out-of-order]
        first_argument, third_argument, second_argument
    )
