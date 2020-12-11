# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os


def get_version():
    path = os.path.join(
        os.path.dirname(__file__), 'extruct', 'VERSION')
    with open(path) as f:
        return f.read().strip()


requirements = []

setup(
    name='extruct',
    version=get_version(),
    description='Extract embedded metadata from HTML markup',
    author='Scrapinghub',
    author_email='info@scrapinghub.com',
    maintainer='Scrapinghub',
    maintainer_email='info@scrapinghub.com',
    url='https://github.com/scrapinghub/extruct',
    entry_points={
        'console_scripts': {
            'extruct = extruct.tool:main',
        }
    },
    packages=find_packages(exclude=['tests',]),
    package_data={'extruct': ['VERSION']},
    install_requires=['bleach-extras',
                      'html5lib',
                      'lxml',
                      'rdflib',
                      'rdflib-jsonld',
                      'py-dom-xpath-six',
                      'pyrdfa3',
                      'mf2py',
                      'w3lib',
                      'html-text>=0.5.1',
                      'six',
                      'jstyleson'
                      ],
    extras_require={
        'cli': [
            'requests',
        ],
    },
    keywords='extruct',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
