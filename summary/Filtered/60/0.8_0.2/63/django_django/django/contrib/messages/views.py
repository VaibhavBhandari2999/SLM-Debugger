from django.contrib import messages


class SuccessMessageMixin:
    """
    Add a success message on successful form submission.
    """
    success_message = ''

    def form_valid(self, form):
        """
        Form validation and success message handling for a Django view.
        
        This method is used to handle form validation and success message display after a form is successfully validated. It extends the default form validation behavior by adding a custom success message.
        
        Parameters:
        form (django.forms.Form): The form instance that has been validated.
        
        Returns:
        HttpResponse: The HTTP response object after form validation and message handling.
        
        Key Steps:
        1. Calls the superclass's form_valid method to perform default form validation.
        2. Retrieves the success
        """

        response = super().form_valid(form)
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return response

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data
