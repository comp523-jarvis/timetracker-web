# Generated by Django 2.1.2 on 2018-10-12 18:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('vms', '0004_client'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientAdmin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_created', models.DateTimeField(auto_now_add=True, help_text='The time the admin was created at.', verbose_name='creation time')),
                ('client', models.ForeignKey(help_text='The client company that the user has admin rights to.', on_delete=django.db.models.deletion.CASCADE, related_name='admins', related_query_name='admin', to='vms.Client', verbose_name='client')),
                ('user', models.ForeignKey(help_text='The user who has admin rights on the linked client.', on_delete=django.db.models.deletion.CASCADE, related_name='client_admins', related_query_name='client_admin', to=settings.AUTH_USER_MODEL, verbose_name='admin user')),
            ],
            options={
                'verbose_name': 'client administrator',
                'verbose_name_plural': 'client administrators',
                'ordering': ('client__name', 'time_created'),
            },
        ),
        migrations.AlterUniqueTogether(
            name='clientadmin',
            unique_together={('client', 'user')},
        ),
    ]
