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
        form (django.forms.Form): The form instance that has been validated.
        
        Returns:
        response (HttpResponse): The HTTP response object that should be used for the view.
        
        This method is called when a form is successfully validated. It calls the superclass's form_valid method to handle the form validation and saving. If a success message can be generated from the form's cleaned data
        """

        response = super().form_valid(form)
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return response

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data
