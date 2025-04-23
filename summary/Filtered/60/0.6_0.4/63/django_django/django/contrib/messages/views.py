from django.contrib import messages


class SuccessMessageMixin:
    """
    Add a success message on successful form submission.
    """
    success_message = ''

    def form_valid(self, form):
        """
        Form validation and success message handling method.
        
        This method is overridden to handle form validation and success message display after a form is successfully validated.
        
        Parameters:
        form (Form): The form instance that is being validated.
        
        Returns:
        response (HttpResponse): The HTTP response object.
        
        Key Details:
        - The method first calls the superclass's form_valid method to validate the form.
        - If the form is valid, it retrieves the success message using the get_success_message method.
        - If a success message is found,
        """

        response = super().form_valid(form)
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return response

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data
