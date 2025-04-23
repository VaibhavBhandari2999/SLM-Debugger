from django.contrib import messages


class SuccessMessageMixin:
    """
    Add a success message on successful form submission.
    """
    success_message = ''

    def form_valid(self, form):
        """
        Form validation and success message handling for a Django view.
        
        This method is used to handle form validation in a Django view. It first calls the superclass's form_valid method to process the form. Then, it checks if a success message should be displayed based on the form's cleaned data. If a success message is found, it is added to the messages framework for the request. Finally, the method returns the response from the superclass's form_valid method.
        
        Parameters:
        form (django.forms.Form): The
        """

        response = super().form_valid(form)
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return response

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data
