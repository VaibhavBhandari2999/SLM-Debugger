import functools

from django.http import HttpRequest


def sensitive_variables(*variables):
    """
    Indicate which variables used in the decorated function are sensitive so
    that those variables can later be treated in a special way, for example
    by hiding them when logging unhandled exceptions.

    Accept two forms:

    * with specified variable names:

        @sensitive_variables('user', 'password', 'credit_card')
        def my_function(user):
            password = user.pass_word
            credit_card = user.credit_card_number
            ...

    * without any specified variable names, in which case consider all
      variables are sensitive:

        @sensitive_variables()
        def my_function()
            ...
    """
    def decorator(func):
        """
        Decorator function to wrap a given function and handle sensitive variables.
        
        This decorator is designed to be used with other functions to ensure that certain variables are treated as sensitive and are not logged or displayed in error messages. It can be configured to handle all variables or specific ones.
        
        Parameters:
        func (callable): The function to be wrapped.
        
        Returns:
        callable: The wrapped function with added functionality to handle sensitive variables.
        
        Usage:
        @decorator
        def my_function(arg1, arg2):
        """

        @functools.wraps(func)
        def sensitive_variables_wrapper(*func_args, **func_kwargs):
            """
            Wrapper function for handling sensitive variables in a given function.
            
            This function wraps another function to handle sensitive variables. It checks if the `variables` argument is provided and sets the `sensitive_variables` attribute of the wrapper function to the provided variables. If no variables are provided, it sets the attribute to '__ALL__'. The wrapped function is then called with the provided arguments.
            
            Parameters:
            *func_args (tuple): Positional arguments to be passed to the wrapped function.
            **func_kwargs (
            """

            if variables:
                sensitive_variables_wrapper.sensitive_variables = variables
            else:
                sensitive_variables_wrapper.sensitive_variables = '__ALL__'
            return func(*func_args, **func_kwargs)
        return sensitive_variables_wrapper
    return decorator


def sensitive_post_parameters(*parameters):
    """
    Indicate which POST parameters used in the decorated view are sensitive,
    so that those parameters can later be treated in a special way, for example
    by hiding them when logging unhandled exceptions.

    Accept two forms:

    * with specified parameters:

        @sensitive_post_parameters('password', 'credit_card')
        def my_view(request):
            pw = request.POST['password']
            cc = request.POST['credit_card']
            ...

    * without any specified parameters, in which case consider all
      variables are sensitive:

        @sensitive_post_parameters()
        def my_view(request)
            ...
    """
    def decorator(view):
        @functools.wraps(view)
        def sensitive_post_parameters_wrapper(request, *args, **kwargs):
            assert isinstance(request, HttpRequest), (
                "sensitive_post_parameters didn't receive an HttpRequest. "
                "If you are decorating a classmethod, be sure to use "
                "@method_decorator."
            )
            if parameters:
                request.sensitive_post_parameters = parameters
            else:
                request.sensitive_post_parameters = '__ALL__'
            return view(request, *args, **kwargs)
        return sensitive_post_parameters_wrapper
    return decorator
