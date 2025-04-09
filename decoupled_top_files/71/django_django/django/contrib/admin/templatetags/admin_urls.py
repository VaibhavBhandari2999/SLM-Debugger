"""
```markdown
This Python file contains Django template tags and a utility function for generating URLs with preserved filters for admin changelist views. It includes:

- `admin_urlname`: A filter that generates an admin URL name based on model app label and model name.
- `admin_urlquote`: A filter that URL encodes a given value.
- `add_preserved_filters`: A template tag that modifies a URL to preserve filters for an admin changelist view, handling popup windows and specific fields.

The `add_preserved_filters` function interacts with the Django admin context to merge preserved filters with the query string of a given URL, ensuring that the URL retains relevant filters when navigating within the admin interface.
```

### Explanation:
- **Purpose**: The
"""
from urllib.parse import parse_qsl, unquote, urlparse, urlunparse

from django import template
from django.contrib.admin.utils import quote
from django.urls import Resolver404, get_script_prefix, resolve
from django.utils.http import urlencode

register = template.Library()


@register.filter
def admin_urlname(value, arg):
    return 'admin:%s_%s_%s' % (value.app_label, value.model_name, arg)


@register.filter
def admin_urlquote(value):
    return quote(value)


@register.simple_tag(takes_context=True)
def add_preserved_filters(context, url, popup=False, to_field=None):
    """
    Generates a URL with preserved filters for an admin changelist view.
    
    Args:
    context (dict): The context dictionary containing the admin view's context.
    url (str): The URL to be modified.
    popup (bool, optional): Whether the URL is for a popup window. Defaults to False.
    to_field (str, optional): The related field name for filtering. Defaults to None.
    
    Returns:
    str: The modified URL with preserved filters.
    
    Important Functions:
    """

    opts = context.get('opts')
    preserved_filters = context.get('preserved_filters')

    parsed_url = list(urlparse(url))
    parsed_qs = dict(parse_qsl(parsed_url[4]))
    merged_qs = {}

    if opts and preserved_filters:
        preserved_filters = dict(parse_qsl(preserved_filters))

        match_url = '/%s' % unquote(url).partition(get_script_prefix())[2]
        try:
            match = resolve(match_url)
        except Resolver404:
            pass
        else:
            current_url = '%s:%s' % (match.app_name, match.url_name)
            changelist_url = 'admin:%s_%s_changelist' % (opts.app_label, opts.model_name)
            if changelist_url == current_url and '_changelist_filters' in preserved_filters:
                preserved_filters = dict(parse_qsl(preserved_filters['_changelist_filters']))

        merged_qs.update(preserved_filters)

    if popup:
        from django.contrib.admin.options import IS_POPUP_VAR
        merged_qs[IS_POPUP_VAR] = 1
    if to_field:
        from django.contrib.admin.options import TO_FIELD_VAR
        merged_qs[TO_FIELD_VAR] = to_field

    merged_qs.update(parsed_qs)

    parsed_url[4] = urlencode(merged_qs)
    return urlunparse(parsed_url)
