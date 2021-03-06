# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('patchwork', '0002_fix_patch_state_default_values'),
    ]

    operations = [
        migrations.CreateModel(
            name='Check',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=datetime.datetime.now)),
                ('state', models.SmallIntegerField(default=0, help_text=b'The state of the check.', choices=[(0, b'pending'), (1, b'success'), (2, b'warning'), (3, b'fail')])),
                ('target_url', models.URLField(help_text=b'The target URL to associate with this check. This should be specific to the patch.', null=True, blank=True)),
                ('description', models.TextField(help_text=b'A brief description of the check.', null=True, blank=True)),
                ('context', models.CharField(default=b'default', max_length=255, null=True, help_text=b'A label to discern check from checks of other testing systems.', blank=True)),
                ('patch', models.ForeignKey(to='patchwork.Patch')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
