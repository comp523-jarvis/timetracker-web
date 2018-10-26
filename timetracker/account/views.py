import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import generic
from django.views.generic import TemplateView

from account import forms


logger = logging.getLogger(__name__)


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    View the authenticated user's profile.
    """
    template_name = 'account/profile.html'


class SignUpView(generic.FormView):
    """
    View to register new users.
    """
    form_class = forms.SignUpForm
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        """
        Save the signup form and log in the created user.

        Args:
            form:
                The form containing the data sent to the view.

        Returns:
            A redirect response sending the new user to their profile
            page.
        """
        form.save()

        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=raw_password)
        login(self.request, user)

        logger.info('Registered new user %r', user)

        return redirect('account:profile')
