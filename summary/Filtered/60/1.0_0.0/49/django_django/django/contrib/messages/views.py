from django.contrib import messages


class SuccessMessageMixin:
    """
    Add a success message on successful form submission.
    """
    success_message = ''

    def form_valid(self, form):
        """
        form_valid(form)
        
        Generate a success message and display it using Django's message framework after a form is successfully validated.
        
        Parameters:
        form (django.forms.Form): The form instance that is being validated.
        
        Returns:
        response (HttpResponse): The HTTP response object that is returned after the form is successfully validated.
        
        This method extends the default form_valid method by adding a custom success message. If the form is valid, it retrieves the success message using the get_success_message method and displays it to the user
        """

        response = super().form_valid(form)
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return response

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data
