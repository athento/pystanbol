#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='pystanbol',
    version='0.1',
    description='A python REST components for Apache Stanbol',
    author='Athento',
    author_email='rh@athento.com',
    url='https://github.com/athento/hocr-parser',
    license='Apache 2.0 License',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Semantic Tagging'
    ],
    package_dir={'pystanbol': 'src/pystanbol'},
    packages=find_packages('src'),
    install_requires=[
        'restkit',
        'socketpool',
        'rdflib'
    ],
    extras_require={
        'test': [
            'pytest'
        ],
    },
)
