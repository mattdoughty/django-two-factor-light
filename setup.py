from setuptools import setup, find_packages

setup(
    name='django-two-factor-light',
    packages=find_packages(),
    install_requires=[
        'Django>=1.8,<1.9.99'
    ]
)