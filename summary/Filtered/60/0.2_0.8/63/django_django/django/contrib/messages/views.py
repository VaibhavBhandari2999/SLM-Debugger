from django.contrib import messages


class SuccessMessageMixin:
    """
    Add a success message on successful form submission.
    """
    success_message = ''

    def form_valid(self, form):
        """
        Form validation and success message handling for a Django view.
        
        This method is used to handle the form validation process in a Django view. After the form is validated, it checks if a success message should be displayed and adds it to the message framework if available.
        
        Parameters:
        form (django.forms.Form): The form instance that was validated.
        
        Returns:
        django.http.HttpResponse: The response object after form validation, which could be a redirect or a rendered template.
        
        Key Details:
        - The method calls the
        """

        response = super().form_valid(form)
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return response

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data
