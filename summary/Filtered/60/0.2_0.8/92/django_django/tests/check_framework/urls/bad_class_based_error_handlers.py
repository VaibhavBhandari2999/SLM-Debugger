urlpatterns = []


class HandlerView:
    @classmethod
    def as_view(cls):
        """
        Generates a view function for a class. This function is intended to be used as a decorator to create a view function from a class. The view function does not contain any implementation details and is meant to be overridden by subclasses.
        
        Returns:
        function: A view function that can be used as a WSGI application.
        """

        def view():
            pass

        return view


handler400 = HandlerView.as_view()
handler403 = HandlerView.as_view()
handler404 = HandlerView.as_view()
handler500 = HandlerView.as_view()
