from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'vms/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        seconds_worked = sum([emp.total_time for emp in user.employees.all()])
        context['total_hours'] = seconds_worked / (60 * 60)

        return context
