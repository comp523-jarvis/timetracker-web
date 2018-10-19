import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.views.generic import TemplateView
from django.contrib.auth import login, authenticate
from django.shortcuts import redirect
from django.views import generic
from account import forms
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


class SignUpView(generic.FormView):

    form_class = forms.SignUpForm
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        user = form.save()
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=raw_password)
        login(self.request, user)
        return redirect('account:profile')
