from setuptools import setup, find_packages


VERSION = '1.1.0.dev0'


setup(
    name='psu.oit.its.lostandfound',
    version=VERSION,
    description='ITS Lost and Found',
    author='PSU - OIT - WDT',
    author_email='webteam@pdx.edu',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'django>=1.8.12,<1.9',
        'django-arcutils[ldap]>=2.9.1',
        'django-bootstrap-form>=3.2',
        'django-cloak',
        'django-local-settings>=1.0a20',
        'django_pgcli>=0.0.2',
        'psycopg2>=2.6.1',
        'pytz>=2016.3',
    ],
    extras_require={
        'dev': [
            'psu.oit.arc.tasks',
            'coverage',
            'flake8',
            'mock',
            'model-mommy',
        ]
    },
)
