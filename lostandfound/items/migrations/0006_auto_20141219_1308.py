# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0005_auto_20141219_1307'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='found_by_person',
        ),
        migrations.AddField(
            model_name='item',
            name='found_by',
            field=models.ForeignKey(related_name='item_found_by', to='auth.User', null=True),
            preserve_default=True,
        ),
    ]
