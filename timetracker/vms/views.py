from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView

from vms import forms, models


class ClockInView(FormView):
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
            pk=self.kwargs.get('employee_id'),
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
        context['total_hours'] = seconds_worked / (60 * 60)

        return context
