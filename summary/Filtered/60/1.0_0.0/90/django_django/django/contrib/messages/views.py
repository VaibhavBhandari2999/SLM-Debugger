from django.contrib import messages


class SuccessMessageMixin:
    """
    Add a success message on successful form submission.
    """
    success_message = ''

    def form_valid(self, form):
        """
        Form validation and success message handling method.
        
        This method is called when a form is successfully validated. It first calls the superclass's form_valid method to proceed with the default form validation logic. Then, it retrieves the success message based on the form data and adds it to the messages framework if it exists. Finally, it returns the response from the superclass's method.
        
        Parameters:
        form (django.forms.Form): The form instance that has been validated.
        
        Returns:
        HttpResponse: The response object to be returned
        """

        response = super().form_valid(form)
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return response

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data
