from setuptools import setup, find_packages


VERSION = '1.5.0'


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
        'django>=1.11.18,<2.0',
        'django-arcutils[ldap]>=2.24.0',
        'django-bootstrap-form>=3.2.1',
        'django-local-settings>=1.0b7',
        'django_pgcli>=0.0.3',
        'psycopg2>=2.7.6.1',
        'pytz>=2018.7',
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
