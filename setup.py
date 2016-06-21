from setuptools import setup, find_packages


VERSION = '1.1.0'


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
        'django>=1.9.7',
        'django-arcutils[ldap]>=2.10.0',
        'django-bootstrap-form>=3.2.1',
        'django-local-settings>=1.0a20',
        'django_pgcli>=0.0.2',
        'psycopg2>=2.6.1',
        'pytz>=2016.4',
    ],
    extras_require={
        'dev': [
            'psu.oit.arc.tasks',
            'coverage',
            'flake8',
            'model-mommy',
        ]
    },
)
