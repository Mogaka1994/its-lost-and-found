from django.contrib.auth.models import Group

from arcutils.cas.backends import CASModelBackend
from arcutils.ldap import ldapsearch, escape


class ITSCASModelBackend(CASModelBackend):

    def get_or_create_user(self, cas_data, **overrides):
        user = super().get_or_create_user(cas_data, **overrides)

        # Reset on every login in case the user's groups have changed;
        # below we will set these flags as appropriate.
        user.is_active = False
        user.is_staff = False
        user.is_superuser = False

        username = cas_data['username']
        uid = escape(username)

        query = '(cn={uid})'.format(uid=uid)
        results = ldapsearch(query, using='groups')

        # Get the list of groups the user is in.
        member_of = [] if not results else results[0]['member_of']
        groups = [g['name'].lower() for g in member_of]

        if 'its_lab_students_gg' in groups:
            user.is_active = True

        if 'its_cavs_staff_gg' in groups:
            user.is_active = True
            user.is_staff = True

        if 'tlc_gg' in groups:
            user.is_active = True
            user.is_staff = True

        # Automatically add ARC staff as staff & superusers in this app
        query = '(& (memberuid={uid}) (cn=arc))'.format(uid=uid)
        results = ldapsearch(query)
        if results:
            user.is_active = True
            user.is_staff = True
            user.is_superuser = True

        staff_group, _ = Group.objects.get_or_create(name='staff')
        if user.is_staff:
            user.groups.add(staff_group)
        else:
            user.groups.remove(staff_group)

        user.save()
        return user
