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
        This function is a decorator that wraps another function to handle sensitive variables. It accepts a function `func` as its argument and returns a wrapped function `sensitive_variables_wrapper`.
        
        Parameters:
        func (function): The function to be wrapped.
        
        Key Parameters:
        variables (list, optional): A list of variable names that should be treated as sensitive. If not provided, all variables are considered sensitive.
        
        Return:
        function: The wrapped function that includes the logic to handle sensitive variables.
        
        Usage:
        """

        @functools.wraps(func)
        def sensitive_variables_wrapper(*func_args, **func_kwargs):
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
            """
            Wrapper function for a view to mark certain POST parameters as sensitive.
            
            Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments to pass to the view function.
            **kwargs: Additional keyword arguments to pass to the view function.
            
            Keyword Args:
            parameters (list, optional): A list of parameter names to mark as sensitive. If not provided, all POST parameters will be considered sensitive.
            
            Returns:
            The result of the view function.
            
            Raises:
            AssertionError:
            """

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
