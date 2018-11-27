import logging

from django.conf import settings
from django.utils import timezone

from vms import models


logger = logging.getLogger(__name__)


def clock_in(client_id, employee_id, project_id):
    """
    Clock in an employee.

    Args:
        client_id:
            The ID of the client the employee works for.
        employee_id:
            The ID of the employee who is clocking in.
        project_id:
            The ID of the project the employee is working on.

    Returns:
        A response indicating the result of the clock in request.
    """
    try:
        employee = models.Employee.objects.get(
            client__id=client_id,
            employee_id=employee_id,
        )
    except models.Employee.DoesNotExist:
        return (
            'Could not find an employee matching the provided client and '
            'employee IDs.'
        )

    if employee.is_clocked_in:
        return 'You are already clocked in. Please clock out first.'

    try:
        project = models.ClientJob.objects.get(
            client__id=client_id,
            id=project_id,
        )
    except models.ClientJob.DoesNotExist:
        return (
            f'Could not find job {project_id} at {employee.client.name}.'
        )

    models.TimeRecord.objects.create(
        employee=employee,
        job=project,
        pay_rate=project.pay_rate,
    )

    return (
        f'Clocked in {employee.user.name} at {employee.client.name} to job '
        f'{project.name}.'
    )


def clock_out(client_id, employee_id):
    """
    Clock out the employee with the provided information.

    Args:
        client_id:
            The ID of the client that the employee who is clocking out
            works for.
        employee_id:
            The ID of the employee to clock out.

    Returns:
        A string describing the result of the clock out request.
    """
    try:
        employee = models.Employee.objects.get(
            client__id=client_id,
            employee_id=employee_id,
        )
    except models.Employee.DoesNotExist:
        return (
            'Could not find an employee matching the provided client and '
            'employee IDs.'
        )

    if not employee.is_clocked_in:
        return 'You are not clocked in, so no action was taken.'

    time_record = employee.time_records.get(time_end=None)
    time_record.time_end = timezone.now()
    time_record.save()

    return 'You are now clocked out.'


def list_projects(client_id):
    """
    Enumerate the projects for a client.

    Args:
        client_id:
            The ID of the client company whose projects should be
            listed.

    Returns:
        A string message enumerating the projects.
    """
    jobs = models.ClientJob.objects.filter(client__id=client_id)

    project_list = []
    for job in jobs:
        project_list.append(
            f'{job.id} - {job.name}'
        )

    projects = '\n'.join(project_list)

    return f'Select the ID of one of the following projects:\n{projects}'


def process(data):
    intent = data['queryResult']['intent']['name']
    params = data['queryResult']['parameters']

    if intent == settings.DIALOGFLOW_INTENTS['CLOCK_IN']:
        client_id = params['clientID']
        employee_id = params['employeeID']
        project_id = params['jobID']

        return {
            'fulfillmentText': clock_in(client_id, employee_id, project_id),
        }

    elif intent == settings.DIALOGFLOW_INTENTS['CLOCK_OUT']:
        client_id = params['clientID']
        employee_id = params['employeeID']

        return {
            'fulfillmentText': clock_out(client_id, employee_id),
        }

    elif intent == settings.DIALOGFLOW_INTENTS['LIST_PROJECTS']:
        client_id = params['clientID']

        return {
            'fulfillmentText': list_projects(client_id),
        }

    logger.warning('Could not process unknown intent %s', intent)

    return {
        'fulfillmentText': 'Could not understand request. Please try again.'
    }
