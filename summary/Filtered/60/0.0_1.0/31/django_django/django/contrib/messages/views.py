from django.contrib import messages


class SuccessMessageMixin:
    """
    Add a success message on successful form submission.
    """
    success_message = ''

    def form_valid(self, form):
        """
        form_valid(form)
        
        Parameters:
        - form (Form): The form instance that is being validated.
        
        Returns:
        - response (HttpResponse): The HTTP response object that should be used for the view.
        
        This method is called when the form is valid. It first calls the superclass's form_valid method to process the form. Then, it retrieves a success message based on the form data and adds it to the messages framework if a message is found. Finally, it returns the response object from the superclass's method
        """

        response = super().form_valid(form)
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return response

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data
