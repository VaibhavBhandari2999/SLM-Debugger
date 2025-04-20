from django.contrib import messages


class SuccessMessageMixin:
    """
    Add a success message on successful form submission.
    """
    success_message = ''

    def form_valid(self, form):
        """
        Form validation and success message handling method.
        
        This method is called when the form is valid. It first calls the superclass's form_valid method to process the form. Then, it retrieves the success message using the get_success_message method and adds it to the request's messages framework if it exists. Finally, it returns the response from the superclass's method.
        
        Parameters:
        form (Form): The form instance being validated.
        
        Returns:
        HttpResponse: The response from the superclass's form_valid method.
        """

        response = super().form_valid(form)
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return response

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data
