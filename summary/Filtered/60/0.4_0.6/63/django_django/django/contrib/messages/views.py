from django.contrib import messages


class SuccessMessageMixin:
    """
    Add a success message on successful form submission.
    """
    success_message = ''

    def form_valid(self, form):
        """
        Form validation and success message handling for a Django view.
        
        This method is intended to be overridden in a Django view to handle form validation and success message display.
        
        Parameters:
        form (django.forms.Form): The form instance that is being validated.
        
        Returns:
        django.http.HttpResponse: The HTTP response after form validation.
        
        Key Steps:
        1. Calls the superclass's form_valid method to perform the initial form validation.
        2. Retrieves the success message from the form's cleaned data.
        3. Displays the success
        """

        response = super().form_valid(form)
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return response

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data
