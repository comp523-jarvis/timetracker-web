from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView

from vms import forms, models, time_utils


class ClockInView(LoginRequiredMixin, FormView):
    """
    View for clocking in.
    """
    form_class = forms.ClockInForm
    success_url = reverse_lazy('vms:dashboard')
    template_name = 'vms/clock-in.html'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs['employee'] = get_object_or_404(
            models.Employee,
            supervisor__client__slug=self.kwargs.get('client_slug'),
            employee_id=self.kwargs.get('employee_id'),
            user=self.request.user,
        )

        return kwargs


class ClockOutView(LoginRequiredMixin, FormView):
    """
    View for clocking out.
    """
    form_class = forms.ClockOutForm
    success_url = reverse_lazy('vms:dashboard')
    template_name = 'vms/clock-out.html'

    def form_valid(self, form):
        """
        Save the valid form instance.

        Args:
            form:
                The valid form instance.

        Returns:
            A redirect response for the user.
        """
        form.save()

        return super().form_valid(form)

    def get_form_kwargs(self):
        """
        Add the employee as a parameter for the form.

        Returns:
            The kwargs to instantiate the form instance with.
        """
        kwargs = super().get_form_kwargs()

        kwargs['employee'] = get_object_or_404(
            models.Employee,
            supervisor__client__slug=self.kwargs.get('client_slug'),
            employee_id=self.kwargs.get('employee_id'),
            user=self.request.user,
        )

        return kwargs


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'vms/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        employees = self.request.user.employees.all()
        context['employees'] = employees

        clocked_in = any([e.is_clocked_in for e in employees])
        context['clocked_in'] = clocked_in

        seconds_worked = sum([emp.total_time for emp in employees])
        seconds_worked = time_utils.round_time_worked(seconds_worked)
        context['total_hours'] = seconds_worked / (60 * 60)

        return context
