from functools import wraps

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
    if len(variables) == 1 and callable(variables[0]):
        raise TypeError(
            "sensitive_variables() must be called to use it as a decorator, "
            "e.g., use @sensitive_variables(), not @sensitive_variables."
        )

    def decorator(func):
        """
        Decorator function to wrap another function and handle sensitive variables.
        
        This decorator is designed to wrap a function and manage sensitive variables. It can be used to specify which variables are considered sensitive within the wrapped function. If no variables are specified, it defaults to handling all variables as sensitive.
        
        Parameters:
        func (callable): The function to be wrapped.
        
        Returns:
        callable: The wrapped function with added functionality to handle sensitive variables.
        
        Usage:
        @decorator
        def my_function(sensitive_variables=None):
        """

        @wraps(func)
        def sensitive_variables_wrapper(*func_args, **func_kwargs):
            if variables:
                sensitive_variables_wrapper.sensitive_variables = variables
            else:
                sensitive_variables_wrapper.sensitive_variables = "__ALL__"
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
    if len(parameters) == 1 and callable(parameters[0]):
        raise TypeError(
            "sensitive_post_parameters() must be called to use it as a "
            "decorator, e.g., use @sensitive_post_parameters(), not "
            "@sensitive_post_parameters."
        )

    def decorator(view):
        @wraps(view)
        def sensitive_post_parameters_wrapper(request, *args, **kwargs):
            """
            Wrapper function for the sensitive_post_parameters decorator.
            
            This function is designed to be used as a decorator for views in Django. It sets the sensitive_post_parameters attribute on the request object to either a list of parameter names or a special value "__ALL__" if no parameters are specified. This is useful for marking which POST parameters should be treated as sensitive and thus not logged or displayed in error messages.
            
            Parameters:
            request (HttpRequest): The Django HttpRequest object representing the incoming request.
            *args: Additional
            """

            if not isinstance(request, HttpRequest):
                raise TypeError(
                    "sensitive_post_parameters didn't receive an HttpRequest "
                    "object. If you are decorating a classmethod, make sure "
                    "to use @method_decorator."
                )
            if parameters:
                request.sensitive_post_parameters = parameters
            else:
                request.sensitive_post_parameters = "__ALL__"
            return view(request, *args, **kwargs)

        return sensitive_post_parameters_wrapper

    return decorator
