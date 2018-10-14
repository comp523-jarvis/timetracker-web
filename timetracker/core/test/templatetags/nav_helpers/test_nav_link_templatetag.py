from django.test import RequestFactory
from django.urls import reverse
from django.utils.html import format_html

from core.templatetags.nav_helpers import nav_link


HTML_FORMAT_STR = '<li class="nav-item"><a class="{}" href="{}">{}</a></li>'


def test_nav_link_current_page():
    """
    If the current page's URL matches the link's URL, the link should be
    marked as active.
    """
    link_text = 'home'
    url_name = 'home'
    url = reverse(url_name)

    factory = RequestFactory()
    context = {
        'request': factory.get(url),
    }

    expected = format_html(HTML_FORMAT_STR, 'nav-link active', url, link_text)

    assert nav_link(context, link_text, url_name) == expected


def test_nav_link_different_page():
    """
    If the current page's URL does not match the link's URL, the link
    should not be active.
    """
    link_text = 'Dashboard'
    url_name = 'vms:dashboard'
    url = reverse(url_name)

    factory = RequestFactory()
    context = {
        'request': factory.get('/'),
    }

    expected = format_html(HTML_FORMAT_STR, 'nav-link', url, link_text)

    assert nav_link(context, link_text, url_name) == expected
