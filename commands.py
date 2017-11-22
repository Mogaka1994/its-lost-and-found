from runcommands import command

from arctasks.commands import *
from arctasks.django import manage


@command(env='dev', timed=True)
def init(config, overwrite=False, drop_db=False):
    virtualenv(config, overwrite=overwrite)
    install(config)
    createdb(config, drop=drop_db)
    migrate(config)
    manage(config, ('loaddata', 'actions', 'category', 'locations'))
