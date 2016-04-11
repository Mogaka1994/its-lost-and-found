from arctasks import *
from arctasks.django import manage


@arctask(configured='dev', timed=True)
def init(ctx, overwrite=False, drop_db=False):
    virtualenv(ctx, overwrite=overwrite)
    install(ctx)
    createdb(ctx, drop=drop_db)
    migrate(ctx)
    manage(ctx, ('loaddata', 'actions.json', 'category.json', 'locations.json'))
