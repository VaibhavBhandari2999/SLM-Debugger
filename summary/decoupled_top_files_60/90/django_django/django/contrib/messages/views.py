from django.contrib import messages


class SuccessMessageMixin:
    """
    Add a success message on successful form submission.
    """
    success_message = ''

    def form_valid(self, form):
        """
        form_valid(form)
        
        Generate a success message after a form is successfully validated.
        
        Parameters:
        form (django.forms.Form): The form instance that is being validated.
        
        Returns:
        response (HttpResponse): The response object that is returned after the form is successfully validated.
        
        This method is called after the form is successfully validated. It retrieves the success message from the form's cleaned data and displays it using Django's messages framework. If no success message is found, it simply returns the response from the superclass's
        """

        response = super().form_valid(form)
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return response

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data
