from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views import generic
from django.views.generic import DetailView, FormView, ListView, TemplateView
from django.urls import reverse_lazy

from vms import forms, mixins, models, time_utils


class ClientAdminInviteAcceptView(LoginRequiredMixin, generic.FormView):
    """
    Accept in invitation to become an admin for a client.
    """
    form_class = forms.ClientAdminInviteAcceptForm
    template_name = 'vms/client-admin-invite-accept.html'

    def form_valid(self, form):
        """
        Save the form and redirect the user to the detail page of the
        client that the created admin links to.

        Args:
            form:
                The validated form instance to save.

        Returns:
            A redirect response sending the user to the detail view of
            the created admin's client.
        """
        admin = form.save(self.request.user)

        return redirect(admin.client.get_absolute_url())

    def get_form_kwargs(self):
        """
        Get additional keyword arguments for the form.

        Returns:
            The keyword arguments used to initialize the form.
        """
        kwargs = super().get_form_kwargs()

        kwargs['token'] = self.kwargs.get('token')

        return kwargs


class ClientCreateView(UserPassesTestMixin, generic.FormView):
    """
    Create a new client company.
    """
    form_class = forms.ClientCreateForm
    template_name = 'vms/client-create.html'

    def form_valid(self, form):
        """
        Save the form and redirect the user to the newly created
        client's detail page.

        Returns:
            A redirect response sending the user to the detail page of
            the newly created client.
        """
        client = form.save(self.request)

        return redirect(client.get_absolute_url())

    def test_func(self):
        """
        Ensure the requesting user is the administrator of a staffing
        agency.

        Returns:
            A boolean indicating if the user should be allowed to access
            the view.
        """
        if not self.request.user.is_authenticated:
            return False

        return models.StaffingAgencyAdmin.objects.filter(
            user=self.request.user,
        ).exists()


class ClientJobCreateView(LoginRequiredMixin, FormView):
    template_name = 'vms/client-job-create.html'
    form_class = forms.ClientJobCreate

    def form_valid(self, form):
        job = form.save()

        return redirect(job.get_absolute_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        client = get_object_or_404(
            models.Client.objects,
            slug=self.kwargs.get('client_slug')
        )

        context['client'] = client

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs['client'] = get_object_or_404(
            models.Client.objects,
            slug=self.kwargs.get('client_slug'),
        )

        return kwargs


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
            client__slug=self.kwargs.get('client_slug'),
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
            context['staff_admins'] = adminagency

        if models.ClientAdmin.objects.filter(
                user=self.request.user).exists():
            client_admins = models.ClientAdmin.objects.filter(
                user=self.request.user).all()
            context['client_admins'] = client_admins

        clocked_in = any([e.is_clocked_in for e in employees])
        context['clocked_in'] = clocked_in

        seconds_worked = sum([emp.total_time for emp in employees])
        seconds_worked = time_utils.round_time_worked(seconds_worked)
        total_hours = seconds_worked / (60 * 60)
        context['total_hours'] = total_hours

        return context


class ClientDetailView(DetailView):
    """
    Retrieve information about a specific client.
    """
    context_object_name = 'client'
    template_name = 'vms/client-detail.html'

    def get_context_data(self, **kwargs):
        """
        Get additional context to render the template with.

        Args:
            **kwargs:
                Additional values to be passed to the template.

        Returns:
            A dictionary containing the context used to render the
            view's template.
        """
        context = super().get_context_data(**kwargs)

        context['active_employees'] = self.object.employees.filter(
            is_active=True,
        ).count()

        context['is_admin'] = (
            self.request.user.is_authenticated and self.object.admins.filter(
                user=self.request.user,
            ).exists()
        )

        context['job_count'] = self.object.jobs.count()

        total_time = models.TimeRecord.objects.filter(
            employee__client=self.object,
        ).total_time()
        context['total_hours'] = total_time.total_seconds() / (60 * 60)

        return context

    def get_object(self, queryset=None):
        """
        Get the client whose slug is specified in the URL.

        Args:
            queryset:
                The queryset to choose a client from. If a queryset is
                not provided, all clients are searched.

        Returns:
            The client with the slug given in the URL.
        """
        queryset = queryset or models.Client.objects.all()

        return get_object_or_404(
            queryset,
            slug=self.kwargs.get('client_slug'),
        )


class EmployeeApplyView(LoginRequiredMixin, generic.FormView):
    """
    Apply a staffing agency employee to a client company.
    """
    form_class = forms.EmployeeApplyForm
    template_name = 'vms/staffing-agency-employee-apply.html'

    def form_valid(self, form):
        """
        Save the form and redirect back to the staffing agency detail
        view.

        Args:
            form:
                The form to save.
        Returns:
            A response redirecting the user to the staffing agency's
            detail view.
        """
        employee = form.save()

        return redirect(employee.staffing_agency.get_absolute_url())

    def get_context_data(self, **kwargs):
        """
        Get additional context used to render the view's template.

        Args:
            **kwargs:

        Returns:
            A dictionary containing the context used to render the
            view's template.
        """
        context = super().get_context_data(**kwargs)

        context['available_clients'] = models.Client.objects.exclude(
            employee__staffing_agency=context['form'].staffing_agency,
            employee__user=context['form'].user,
        )

        context['employee'] = get_object_or_404(
            models.StaffingAgencyEmployee,
            agency__admin__user=self.request.user,
            agency__slug=self.kwargs.get('staffing_agency_slug'),
            id=self.kwargs.get('employee_id'),
        )

        return context

    def get_form_kwargs(self):
        """
        Get the keyword arguments to initialize the form with.

        Returns:
            A dictionary containing the arguments to initialize the
            view's form instance with.
        """
        kwargs = super().get_form_kwargs()

        agency = get_object_or_404(
            models.StaffingAgency,
            admin__user=self.request.user,
            slug=self.kwargs.get('staffing_agency_slug'),
        )

        staff_employee = get_object_or_404(
            agency.employees,
            id=self.kwargs.get('employee_id'),
        )

        kwargs['staffing_agency'] = agency
        kwargs['user'] = staff_employee.user

        return kwargs


class EmployeeApproveView(LoginRequiredMixin, FormView):
    """
    Can link a supervisor to an approved employee.
    """
    template_name = 'vms/employee-approval.html'
    form_class = forms.EmployeeApprovalForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs['employee'] = get_object_or_404(
            models.Employee,
            client__slug=self.kwargs.get('client_slug'),
            employee_id=self.kwargs.get('employee_id')
        )

        return kwargs

    def form_valid(self, form):
        admin = get_object_or_404(
            models.ClientAdmin,
            client__slug=self.kwargs.get('client_slug'),
            user=self.request.user
        )
        form.save(admin)

        return redirect(
            'vms:employee-pending',
            client_slug=admin.client.slug,
        )


class EmployeeDetailView(
    mixins.DateRangeMixin,
    LoginRequiredMixin,
    generic.DetailView,
):
    """
    View the details of a single employee.
    """
    context_object_name = 'employee'
    template_name = 'vms/employee-detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        shown_time_records = self.filter_by_date(
            self.object.time_records.all(),
        )

        open_time_record = self.object.time_records.filter(
            time_end=None,
        ).first()

        context['open_time_record'] = open_time_record
        context['is_employee'] = self.object.user == self.request.user

        is_client_admin = models.ClientAdmin.objects.filter(
            client=self.object.client,
            user=self.request.user,
        ).exists()
        context['is_client_admin'] = is_client_admin

        unapproved_count = shown_time_records.filter(
            approval=None,
        ).exclude(
            time_end=None,
        ).count()
        context['unapproved_count'] = unapproved_count

        seconds_worked = shown_time_records.total_time().total_seconds()
        seconds_worked = time_utils.round_time_worked(seconds_worked)
        total_hours = seconds_worked / (60 * 60)
        context['total_hours'] = total_hours

        context['shown_time_records'] = shown_time_records

        return context

    def get_object(self, queryset=None):
        """
        Get the employee using the parameters in the URL.

        Args:
            queryset:
                The queryset to pull from. If not provided, all
                employees are searched.

        Returns:
            The employee with the ID and client slug specifieid in the
            URL.
        """
        is_self = Q(user=self.request.user)
        is_staffer = Q(staffing_agency__admin__user=self.request.user)
        is_supervisor = Q(client__admin__user=self.request.user)

        employees = models.Employee.objects.filter(
            is_self | is_staffer | is_supervisor,
        ).distinct()

        return get_object_or_404(
            employees,
            client__slug=self.kwargs.get('client_slug'),
            employee_id=self.kwargs.get('employee_id'),
        )


class PendingEmployeesView(LoginRequiredMixin, ListView):
    """
    Can see the list of pending employees that need to be approved or stopped
    """
    context_object_name = 'pending_employees'
    template_name = 'vms/employee-pending.html'

    def get_queryset(self):
        """
        Get the jobs for the specified client.

        Returns:
            The jobs owned by the client whose slug is given in the URL.
        """
        client = get_object_or_404(
            models.Client,
            slug=self.kwargs.get('client_slug'),
            admin__user=self.request.user,
        )
        return client.employees.filter(time_approved=None)


class StaffingAgencyDetailView(generic.DetailView):
    """
    Retrieve information about a specific staffing agency.
    """
    context_object_name = 'staffing_agency'
    template_name = 'vms/staffing-agency.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['is_admin'] = (
            self.request.user.is_authenticated
            and self.object.admins.filter(
                user=self.request.user,
            ).exists()
        )

        return context

    def get_object(self, **kwargs):
        return get_object_or_404(
            models.StaffingAgency,
            slug=self.kwargs.get('staffing_agency_slug'),
        )


class StaffingAgencyEmployeeApproveView(LoginRequiredMixin, generic.FormView):
    """
    Approve an employee who has applied to a staffing agency.
    """
    form_class = forms.StaffingAgencyEmployeeApprovalForm

    def form_valid(self, form):
        """
        Save the form and redirect the user.

        Args:
            form:
                The form to save.

        Returns:
            A response redirecting the user. If a ``next`` parameter is
            provided in the URL, the user is redirected there. Otherwise
            they are redirected to the list of pending employees.
        """
        form.save()

        redirect_url = self.request.GET.get('next')
        if redirect_url is not None:
            return redirect(redirect_url)

        return redirect(
            'vms:staffing-agency-employee-pending',
            staffing_agency_slug=form.employee.agency.slug,
        )

    def get_form_kwargs(self):
        """
        Returns:
            A dictionary containing the keyword arguments used to
            instantiate the view's form class.
        """
        kwargs = super().get_form_kwargs()

        kwargs['admin'] = get_object_or_404(
            models.StaffingAgencyAdmin,
            agency__slug=self.kwargs.get('staffing_agency_slug'),
            user=self.request.user,
        )

        kwargs['employee'] = get_object_or_404(
            models.StaffingAgencyEmployee,
            id=self.kwargs.get('employee_id'),
        )

        return kwargs


class StaffingAgencyEmployeeCreateView(LoginRequiredMixin, FormView):
    """
    Apply as an employee to a staffing agency.
    """
    form_class = forms.StaffingAgencyEmployeeCreateForm
    success_url = reverse_lazy('vms:dashboard')
    template_name = 'vms/staffing-agency-apply.html'

    def form_valid(self, form):
        """
        Save the form and redirect the user.

        Args:
            form:
                The form to save.

        Returns:
            A response redirecting the user to their dashboard.
        """
        form.save(self.request.user)

        return super().form_valid(form)

    def get_form_kwargs(self):
        """
        Get the keyword arguments used to instantiate the form.

        Returns:
            A dictionary containing the arguments used to instantiate an
            instance of the view's form class.
        """
        kwargs = super().get_form_kwargs()

        kwargs['user'] = self.request.user

        return kwargs


class StaffingAgencyEmployeeDetailView(LoginRequiredMixin, generic.DetailView):
    context_object_name = 'employee'
    template_name = 'vms/staffing-agency-employee.html'

    def get_context_data(self, **kwargs):
        """
        Get context data to render the view's template with.

        Args:
            **kwargs:

        Returns:
            A dictionary containing context to render the view's
            template with.
        """
        context = super().get_context_data(**kwargs)

        context['client_employees'] = models.Employee.objects.filter(
            staffing_agency=self.object.agency,
            user=self.object.user,
        )

        return context

    def get_object(self, *args, **kwargs):
        """
        Returns:
            The staffing agency employee whose ID is specified in the
            URL.
        """
        return get_object_or_404(
            models.StaffingAgencyEmployee,
            agency__admin__user=self.request.user,
            agency__slug=self.kwargs.get('staffing_agency_slug'),
            id=self.kwargs.get('employee_id'),
        )


class StaffingAgencyEmployeePendingListView(
    LoginRequiredMixin,
    generic.ListView,
):
    """
    List the pending employees for a staffing agency.
    """
    context_object_name = 'employees'
    template_name = 'vms/staffing-agency-employee-pending.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._agency = None

    def get_context_data(self, *args, **kwargs):
        """
        Returns:
            The context used to render the view's template.
        """
        context = super().get_context_data(*args, **kwargs)

        context['agency'] = self._agency

        return context

    def get_queryset(self):
        """
        Returns:
            A queryset containing the pending employees for the staffing
            agency whose slug is given in the URL.
        """
        self._agency = get_object_or_404(
            models.StaffingAgency,
            admin__user=self.request.user,
            slug=self.kwargs.get('staffing_agency_slug'),
        )

        return self._agency.employees.filter(time_approved=None)


class TimeRecordApproveView(LoginRequiredMixin, generic.FormView):
    """
    Approve a specific time record.
    """
    form_class = forms.TimeRecordApprovalForm

    def form_valid(self, form):
        """
        Save the form and redirect back to the hours approval page.

        Args:
            form:
                The valid form instance to save.

        Returns:
            A redirect response. If a 'next' parameter is provided in
            the URL, the user is taken to that URL. Otherwise they are
            taken to the list of unapproved hours for the client who
            owns the time record that was just approved.
        """
        approval = form.save()

        next_url = self.request.GET.get('next')
        if next_url:
            return redirect(next_url)

        # No redirect specified, default to unapproved hours list.
        client = approval.time_record.employee.client

        return redirect(
            client.unapproved_time_record_list_url
        )

    def get_form_kwargs(self):
        """
        Add additional information required for our custom form.

        Returns:
            The keyword arguments used to construct the form.
        """
        kwargs = super().get_form_kwargs()

        kwargs['approving_user'] = self.request.user
        kwargs['time_record'] = get_object_or_404(
            models.TimeRecord,
            employee__client__admin__user=self.request.user,
            id=self.kwargs.get('time_record_id'),
        )

        return kwargs


class UnapprovedTimeRecordListView(LoginRequiredMixin, generic.ListView):
    """
    List all the unapproved time records for a specific client.
    """
    context_object_name = 'time_records'
    template_name = 'vms/unapproved-hours-list.html'

    def get_queryset(self):
        """
        Get the list of unapproved hours for the client.

        Returns:
            A queryset containing the unapproved time records for the
            client specified in the URL.
        """
        client = get_object_or_404(
            models.Client,
            admin__user=self.request.user,
            slug=self.kwargs.get('client_slug'),
        )

        return models.TimeRecord.objects.exclude(
            time_end=None,
        ).filter(
            approval=None,
            employee__client=client,
        ).order_by(
            '-time_start',
        )
