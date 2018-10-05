import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.views.generic import TemplateView


logger = logging.getLogger(__name__)


class LoginView(BaseLoginView):
    """
    Custom login view to set the user's timezone.
    """
    template_name = 'registration/login.html'

    def form_valid(self, form):
        """
        Save the user's timezone in the session when the user
        authenticates.

        Args:
            form:
                The login form that was validated.

        Returns:
            A redirect response for the user.
        """
        response = super().form_valid(form)

        self.request.session['django_timezone'] = form.get_user().timezone
        logger.debug(
            'Set timezone for %r to %s',
            form.get_user(),
            form.get_user().timezone,
        )

        return response


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    View the authenticated user's profile.
    """
    template_name = 'account/profile.html'
