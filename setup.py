from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='code',
    version='0.0.1',
    packages=find_packages(),
    install_requires=requirements
)