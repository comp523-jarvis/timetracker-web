from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    View the authenticated user's profile.
    """
    template_name = 'account/profile.html'
