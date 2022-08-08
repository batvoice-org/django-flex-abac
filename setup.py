from setuptools import setup, find_packages

def get_version():
    with open("VERSION", "r") as f:
        version = f.read().replace("\n", "").replace(" ", "")
        print("version", version)
    return version

setup(
    python_requires=">=3.6",
    version=get_version(),
    include_package_data=True,
    packages=find_packages(exclude=['docs', "*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=[
        'Django >= 2.2.12',
        'django-extensions >= 3.1.0',
        'django-rest-polymorphic==0.1.9',
        'django-filter >= 2.4.0',
        'django-treebeard >= 4.3.1',
        'djangorestframework >= 3.12.2',
        'factory-boy >= 3.1.0',
        'Faker >= 5.0.1',
        'importlib-metadata >= 3.3.0',
        'Markdown >= 3.3.3',
        'python-dateutil >= 2.8.1',
        'pytz >= 2020.4',
        'PyYAML >= 5.3.1',
        'six >= 1.15.0',
        'sqlparse >= 0.4.1',
        'text-unidecode >= 1.3',
        'typing-extensions >= 3.7.4.3',
        'zipp >= 3.4.0',
        'psycopg2 >= 2.8.6',
        'django-picklefield >= 3.0.1',
        'django-cors-headers >= 3.7.0',
        'jsonfield >= 3.1.0',
        'django-allauth >= 0.41.0'
    ],
    extras_require={
        'doc': [
            'sphinx >= 4.2.0',
            'sphinx-rtd-theme >= 1.0.0',
            'livereload >= 2.6.3',
            'sphinxcontrib-httpdomain >= 1.8.0',
            'MarkupSafe < 2.1.0'
        ],
    },
)

