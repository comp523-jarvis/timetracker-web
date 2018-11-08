from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import TemplateView, FormView, DetailView

from vms import forms, models, time_utils


class ClientJobDetailView(LoginRequiredMixin, generic.UpdateView):
    """
    View or update the details of a specific client job.
    """
    context_object_name = 'job'
    fields = ('pay_rate', 'description')
    template_name = 'vms/client-job-detail.html'

    def get_object(self, queryset=None):
        """
        Get the job specified by the client and job present in the URL.

        Args:
            queryset:
                An optional queryset to choose from. If no queryset is
                provided, all client jobs will be searched.

        Returns:
            The client job specified by the client and jobs slugs in the
            URL.
        """
        if queryset is None:
            queryset = models.ClientJob.objects.all()

        return get_object_or_404(
            queryset,
            client__admin__user=self.request.user,
            client__slug=self.kwargs.get('client_slug'),
            slug=self.kwargs.get('job_slug'),
        )


class ClientJobListView(LoginRequiredMixin, generic.ListView):
    """
    List the jobs for a particular client.
    """
    context_object_name = 'jobs'
    template_name = 'vms/client-job-list.html'

    def __init__(self):
        """
        Initialize the client to ``None``.
        """
        super().__init__()

        self._client = None

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Get the context to render the template with.

        Args:
            object_list:
                The list of client jobs rendered by the view.
            **kwargs:
                Additional context variables for the template.

        Returns:
            A dictionary containing the context used to render the
            view's template.
        """
        context = super().get_context_data(object_list=object_list, **kwargs)

        context['client'] = self._client

        return context

    def get_queryset(self):
        """
        Get the jobs for the specified client.

        Returns:
            The jobs owned by the client whose slug is given in the URL.
        """
        self._client = get_object_or_404(
            models.Client,
            admin__user=self.request.user,
            slug=self.kwargs.get('client_slug'),
        )

        return self._client.jobs.all()


class ClockInView(LoginRequiredMixin, FormView):
    """
    View for clocking in.
    """
    form_class = forms.ClockInForm
    template_name = 'vms/clock-in.html'

    def form_valid(self, form):
        form.save()
        return redirect(
            'vms:employee-dash',
            client_slug=form.employee.client.slug,
            employee_id=form.employee.employee_id,
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs['employee'] = get_object_or_404(
            models.Employee,
            client__slug=self.kwargs.get('client_slug'),
            employee_id=self.kwargs.get('employee_id'),
            user=self.request.user,
        )

        return kwargs


class ClockOutView(LoginRequiredMixin, FormView):
    """
    View for clocking out.
    """
    form_class = forms.ClockOutForm
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

        return redirect(
            'vms:employee-dash',
            client_slug=form.employee.client.slug,
            employee_id=form.employee.employee_id,
        )

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

        if models.StaffingAgencyAdmin.objects.filter(
                user=self.request.user).exists():
            adminagency = models.StaffingAgencyAdmin.objects.filter(
                user=self.request.user)
            context['staff_admin'] = adminagency

        clocked_in = any([e.is_clocked_in for e in employees])
        context['clocked_in'] = clocked_in

        seconds_worked = sum([emp.total_time for emp in employees])
        seconds_worked = time_utils.round_time_worked(seconds_worked)
        total_hours = seconds_worked / (60 * 60)
        context['total_hours'] = total_hours

        return context


class CreateStaffAgencyView(LoginRequiredMixin, FormView):
    """
    View for creating a staffing agency
    """
    form_class = forms.CreateStaffAgencyForm
    success_url = reverse_lazy('vms:dashboard')
    template_name = 'vms/create-staff-agency.html'

    def form_valid(self, form):
        form.save(self.request.user)
        return super().form_valid(form)


class EmployeeDashView(LoginRequiredMixin, TemplateView):
    template_name = 'vms/employee-dash.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        employee = models.Employee.objects.get(
            client__slug=self.kwargs.get('client_slug'),
            employee_id=self.kwargs.get('employee_id'),
        )
        context['employee'] = employee

        seconds_worked = employee.total_time
        seconds_worked = time_utils.round_time_worked(seconds_worked)
        total_hours = seconds_worked / (60 * 60)
        context['total_hours'] = total_hours

        return context


class ClientView(DetailView):
    context_object_name = 'client'
    template_name = 'vms/clientview.html'

    def get_object(self):
        return get_object_or_404(
            models.Client,
            slug=self.kwargs.get('client_slug'))
