from django import template
from django.urls import reverse
from django.utils.html import format_html


register = template.Library()


@register.simple_tag(takes_context=True)
def nav_link(context, link_text, url_name, *url_args):
    """
    Create a navbar link from a reversed url.

    If the URL corresponds to the current page, the link will be marked
    as active.

    Args:
        context:
            The current view context. Used to fetch the current path.
        link_text:
            The text to display in the navigation link.
        url_name:
            The name of the URL to reverse.
        *url_args:
            Any additional arguments used to reverse the URL.

    Returns:
        An HTML snippet containing the code for the navbar link.
    """
    current_path = context['request'].path
    url = reverse(url_name, *url_args)

    link_classes = 'nav-link' if current_path != url else 'nav-link active'
    html_format_str = (
        '<li class="nav-item"><a class="{}" href="{}">{}</a></li>'
    )

    return format_html(html_format_str, link_classes, url, link_text)
