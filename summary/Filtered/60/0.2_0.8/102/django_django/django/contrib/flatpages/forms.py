from django import forms
from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from django.core.exceptions import ValidationError
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _


class FlatpageForm(forms.ModelForm):
    url = forms.RegexField(
        label=_("URL"),
        max_length=100,
        regex=r"^[-\w/\.~]+$",
        help_text=_(
            "Example: “/about/contact/”. Make sure to have leading and trailing "
            "slashes."
        ),
        error_messages={
            "invalid": _(
                "This value must contain only letters, numbers, dots, "
                "underscores, dashes, slashes or tildes."
            ),
        },
    )

    class Meta:
        model = FlatPage
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        """
        Initialize the URL field with a help text that includes an example URL with a leading slash. This method is called during the object's initialization.
        
        Parameters:
        *args: Additional positional arguments passed to the superclass initializer.
        **kwargs: Additional keyword arguments passed to the superclass initializer.
        
        Note:
        - The help text for the URL field is set to guide users on the correct format, specifically mentioning the need for a leading slash.
        - The help text is only applied if the `_trailing_slash_required
        """

        super().__init__(*args, **kwargs)
        if not self._trailing_slash_required():
            self.fields["url"].help_text = _(
                "Example: “/about/contact”. Make sure to have a leading slash."
            )

    def _trailing_slash_required(self):
        return (
            settings.APPEND_SLASH
            and "django.middleware.common.CommonMiddleware" in settings.MIDDLEWARE
        )

    def clean_url(self):
        url = self.cleaned_data["url"]
        if not url.startswith("/"):
            raise ValidationError(
                gettext("URL is missing a leading slash."),
                code="missing_leading_slash",
            )
        if self._trailing_slash_required() and not url.endswith("/"):
            raise ValidationError(
                gettext("URL is missing a trailing slash."),
                code="missing_trailing_slash",
            )
        return url

    def clean(self):
        """
        Ensures that a flatpage with the same URL does not already exist for any of the specified sites.
        
        This method is intended to be used as part of a form's clean method to validate that a new flatpage URL is unique across specified sites. It checks if a URL already exists in the database for the given sites, excluding the current instance if it exists.
        
        Parameters:
        - url (str): The URL of the flatpage to be validated.
        - sites (QuerySet): A queryset
        """

        url = self.cleaned_data.get("url")
        sites = self.cleaned_data.get("sites")

        same_url = FlatPage.objects.filter(url=url)
        if self.instance.pk:
            same_url = same_url.exclude(pk=self.instance.pk)

        if sites and same_url.filter(sites__in=sites).exists():
            for site in sites:
                if same_url.filter(sites=site).exists():
                    raise ValidationError(
                        _("Flatpage with url %(url)s already exists for site %(site)s"),
                        code="duplicate_url",
                        params={"url": url, "site": site},
                    )

        return super().clean()
()
