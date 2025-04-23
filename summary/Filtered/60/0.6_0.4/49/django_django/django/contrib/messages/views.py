from django.contrib import messages


class SuccessMessageMixin:
    """
    Add a success message on successful form submission.
    """
    success_message = ''

    def form_valid(self, form):
        """
        form_valid(form)
        
        This method is overridden to customize the form validation process for a Django view.
        
        Parameters:
        - form (django.forms.Form): The form instance that has been validated and is about to be saved.
        
        Returns:
        - response (HttpResponse): The HTTP response to be returned after the form is successfully validated and saved.
        
        This method first calls the superclass's form_valid method to perform the default form validation and saving process. If the form is valid, it retrieves a success message using the get_success
        """

        response = super().form_valid(form)
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return response

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data
