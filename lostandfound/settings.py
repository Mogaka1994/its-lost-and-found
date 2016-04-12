from arcutils.settings import init_settings

from local_settings import SecretSetting

LDAP = {
    'groups': {
        'password': SecretSetting(doc='Active Directory password'),
    }
}

init_settings()
