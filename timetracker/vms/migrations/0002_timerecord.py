# Generated by Django 2.1.2 on 2018-10-04 00:59

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('vms', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimeRecord',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, help_text='A unique identifier for the time record.', primary_key=True, serialize=False, unique=True, verbose_name='ID')),
                ('is_approved', models.BooleanField(default=False, help_text="A boolean indicating if the time record has been approved by the employee's manager.", verbose_name='is approved')),
                ('time_end', models.DateTimeField(blank=True, help_text='The ending time of the work period.', null=True, verbose_name='end time')),
                ('time_start', models.DateTimeField(default=django.utils.timezone.now, help_text='The start time of the work period.', verbose_name='start time')),
                ('employee', models.ForeignKey(help_text='The employee who worked during this time period.', on_delete=django.db.models.deletion.CASCADE, related_name='time_records', related_query_name='time_record', to='vms.Employee', verbose_name='employee')),
            ],
            options={
                'verbose_name': 'time record',
                'verbose_name_plural': 'time records',
                'ordering': ('time_start',),
            },
        ),
    ]
