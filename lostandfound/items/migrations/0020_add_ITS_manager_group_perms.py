# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-16 22:03
from __future__ import unicode_literals

from django.db import migrations


ITS_MANAGER_PERMISSIONS = (
    ('items', 'location', 'add_location'),
    ('items', 'location', 'change_location'),
    ('items', 'location', 'delete_location'),
    ('items', 'category', 'add_category'),
    ('items', 'category', 'change_category'),
    ('items', 'category', 'delete_category'),
)


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0019_add_long_name_field_to_location'),
    ]

    def add_perms_its_mgr(apps, schema_editor):
        Group = apps.get_model('auth.Group')
        Permission = apps.get_model('auth.Permission')
        ContentType = apps.get_model('contenttypes.ContentType')
        group, _ = Group.objects.get_or_create(name='ITS Manager')

        for perm in ITS_MANAGER_PERMISSIONS:
            content_type, _ = ContentType.objects.get_or_create(app_label=perm[0], model=perm[1])
            permission, _ = Permission.objects.get_or_create(
                content_type=content_type,
                codename=perm[2]
            )
            group.permissions.add(permission)

    def remove_perms_its_mgr(apps, schema_editor):
        Group = apps.get_model('auth.Group')
        Permission = apps.get_model('auth.Permission')
        ContentType = apps.get_model('contenttypes.ContentType')
        group, _ = Group.objects.get_or_create(name='ITS Manager')

        for perm in ITS_MANAGER_PERMISSIONS:
            content_type, _ = ContentType.objects.get_or_create(app_label=perm[0], model=perm[1])
            permission, _ = Permission.objects.get_or_create(
                content_type=content_type,
                codename=perm[2]
            )
            group.permissions.remove(permission)
        group.delete()

    operations = [
            migrations.RunPython(add_perms_its_mgr, remove_perms_its_mgr),
    ]
