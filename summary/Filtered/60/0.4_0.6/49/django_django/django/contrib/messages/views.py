from django.contrib import messages


class SuccessMessageMixin:
    """
    Add a success message on successful form submission.
    """
    success_message = ''

    def form_valid(self, form):
        """
        form_valid(form)
        
        :param form: The form instance that is being validated. This form is expected to be a Django form.
        :type form: django.forms.Form
        
        :returns: A response object, typically a redirect response if the form is valid.
        :rtype: django.http.HttpResponse
        
        This method is overridden to add custom behavior after a form is successfully validated. It calls the superclass's form_valid method to handle the default form validation process. If the form is valid, it retrieves a success message
        """

        response = super().form_valid(form)
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return response

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data
