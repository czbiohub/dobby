#!/usr/bin/env python

from setuptools import setup

version = '1.0.0'

required = open('requirements/default.txt').read().split('\n')

setup(
    name='dobby',
    version=version,
    description='Dobby is the heroic house-elf that automates SampleSheet generation from Google Sheets',
    author='Olga Botvinnik',
    author_email='olga.botvinnik@gmail.com',
    url='https://github.com/czbiohub/dobby',
    packages=['dobby'],
    install_requires=required,
    long_description='See ' + 'https://github.com/czbiohub/dobby',
    license='MIT',
    entry_points={"console_scripts": ['dobby = dobby.cli:cli']}
)
