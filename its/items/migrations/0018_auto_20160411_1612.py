# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0017_add_last_status_view'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='status',
            options={'ordering': ['-timestamp']},
        ),
        migrations.AlterField(
            model_name='item',
            name='is_valuable',
            field=models.BooleanField(help_text='Select this box if the item is an ID, key(s), or is valued at $50 or more. Items valued over $50 are turned into CPSO as soon as possible. Student IDs are turned into the ID services window in the Neuberger Hall Lobby. Checking this box automatically generates an email for the item to be picked up from the lab. USB DRIVES ARE NOT VALUABLE.', default=False),
        ),
    ]
