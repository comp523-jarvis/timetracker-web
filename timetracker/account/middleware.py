from django.utils import timezone
import pytz


class TimezoneMiddleware:
    """
    Class to set the timezone for each request.
    """

    def __init__(self, get_response):
        """
        Initialize the middleware.

        Args:
            get_response:
                A function to get the response from the next middleware
                or the view itself.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Process an incoming request to add timezone information.

        Returns:
            The response from either the view or the next middleware.
        """
        tz = request.session.get('django_timezone', None)

        if tz is None and request.user.is_authenticated:
            tz = request.user.timezone
            request.session['django_timezone'] = tz

        if tz:
            try:
                timezone.activate(tz)
            except pytz.UnknownTimeZoneError:
                timezone.deactivate()
        else:
            timezone.deactivate()

        return self.get_response(request)
