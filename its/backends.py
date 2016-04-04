from django.contrib.auth import get_user_model

from arcutils.ldap import ldapsearch, escape


def cas_response_callback(cas_data):
    username = cas_data['username']
    uid = escape(username)

    user = get_user_model().objects.get(username=username)

    # Reset on every login in case the user's groups have changed; below
    # we will set these flags as appropriate.
    user.is_active = False
    user.is_staff = False
    user.is_superuser = False

    query = '(cn={uid})'.format(uid=uid)
    results = ldapsearch(query, using='groups')

    # Get the list of groups that the user belongs too.
    member_of = results[0][1]['memberOf']
    member_of = ', '.join(member_of).lower()

    if 'cn=its_lab_students_gg' in member_of:
        user.is_active = True

    if 'cn=its_cavs_staff_gg' in member_of:
        user.is_active = True
        user.is_staff = True

    if 'cn=tlc_gg' in member_of:
        user.is_active = True
        user.is_staff = True

    # Automatically add ARC staff as staff & superusers in this app
    query = '(& (memberuid={uid}) (cn=arc))'.format(uid=uid)
    results = ldapsearch(query)
    if results:
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True

    user.save()
    return user
