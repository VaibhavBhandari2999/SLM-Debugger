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
        Decorator to mark a view function or class to mark POST parameters as sensitive.
        
        This decorator is used to mark a view function or class to treat certain POST parameters as sensitive, which can be useful for logging or security purposes. The decorator takes a single argument `parameters`, which is a list of parameter names to be marked as sensitive.
        
        Parameters:
        view (function or class): The view function or class to be decorated.
        
        Returns:
        function: A wrapped function or class that includes the sensitive_post_parameters
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
            Wrapper function for sensitive_post_parameters decorator.
            
            This function is designed to be used as a decorator for views in Django applications. It ensures that the request object is an instance of HttpRequest and sets the sensitive_post_parameters attribute on the request object. If parameters are provided, it assigns them to the request's sensitive_post_parameters attribute; otherwise, it assigns "__ALL__" to indicate that all post parameters are sensitive.
            
            Parameters:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments
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
meters_wrapper

    return decorator
