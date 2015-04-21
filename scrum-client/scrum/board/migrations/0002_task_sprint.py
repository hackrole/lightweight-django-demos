# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='sprint',
            field=models.ForeignKey(blank=True, to='board.Sprint', null=True),
            preserve_default=True,
        ),
    ]
