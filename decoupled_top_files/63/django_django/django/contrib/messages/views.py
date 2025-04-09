"""
The provided Python file contains a Django mixin class named `SuccessMessageMixin`. This mixin is designed to enhance form handling by adding a success message upon successful form submission. It includes methods for validating forms and displaying success messages.

#### Classes Defined:
1. **SuccessMessageMixin**: A Django mixin that extends form handling capabilities by adding success messages.

#### Functions Defined:
1. **form_valid(self, form)**: Validates the form and sets a success message if one is defined. It then displays the success message using Django's messaging framework.
2. **get_success_message(self, cleaned_data)**: Retrieves the success message from the mixin's `success_message` attribute and formats it with the cleaned form data.

#### Key Responsibilities:
- **Adding Success Messages
"""
from django.contrib import messages


class SuccessMessageMixin:
    """
    Add a success message on successful form submission.
    """
    success_message = ''

    def form_valid(self, form):
        """
        Form validation method that processes the form data, sets a success message if available, and returns the response.
        
        Args:
        form (Form): The form instance containing the validated data.
        
        Returns:
        HttpResponse: The HTTP response object after processing the form.
        
        Effects:
        - Calls `super().form_valid(form)` to process the form.
        - Sets a success message using `self.get_success_message(form.cleaned_data)`.
        - Displays the success message using `messages.success(request, success
        """

        response = super().form_valid(form)
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return response

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data
