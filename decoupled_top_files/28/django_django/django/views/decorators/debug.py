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
        This decorator function `decorator` wraps another function `func` to handle sensitive variables. It accepts an optional argument `variables`, which can be a list of variable names or the special value `__ALL__`. If `variables` is provided, it stores these variable names in the `sensitive_variables` attribute of the wrapper function. If no `variables` are specified, all variables are considered sensitive. The wrapped function retains its original name and documentation through the use of `functools.wr
        """

        @functools.wraps(func)
        def sensitive_variables_wrapper(*func_args, **func_kwargs):
            """
            sensitive_variables_wrapper(*func_args, **func_kwargs) -> wrapper function
            
            This function acts as a wrapper around another function, modifying its behavior based on the presence of `variables`. It accepts any number of positional arguments (`*func_args`) and keyword arguments (`**func_kwargs`). The function checks if `variables` is provided; if so, it assigns these variables to the `sensitive_variables` attribute of the wrapper function. If no `variables` are provided, it sets the `
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
            """
            Wrapper function for `view` that sets the `sensitive_post_parameters` attribute on the request object.
            
            Args:
            request (HttpRequest): The HTTP request object.
            view (function): The view function to be wrapped.
            *args: Variable length argument list passed to the view function.
            **kwargs: Arbitrary keyword arguments passed to the view function.
            
            Summary:
            This function is a wrapper for a view function that sets the `sensitive_post_parameters` attribute on the request object
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
