#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function

import os
import sys

from setuptools import setup

pjoin = os.path.join
here = os.path.abspath(os.path.dirname(__file__))

version_label = '1.0.2'

setup_args = dict(
    name                = 'jhub_cas_authenticator',
    packages            = ['jhub_cas_authenticator'],
    version             = version_label,
    description         = """CAS Authenticator: An Authenticator for Jupyterhub that authenticates against an external CAS service.""",
    long_description    = "",
    author              = "Carl (https://github.com/cwaldbieser)",
    author_email        = "",
    url                 = "https://github.com/cwaldbieser/jhub_cas_authenticator",
    license             = "GPLv3",
    platforms           = "Linux, Mac OS X",
    keywords            = ['Interactive', 'Interpreter', 'Shell', 'Web'],
    classifiers         = [
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)

# setuptools requirements
if 'setuptools' in sys.modules:
    setup_args['install_requires'] = install_requires = []
    install_requires.append('jupyterhub')
    install_requires.append('lxml')

def main():
    setup(**setup_args)

if __name__ == '__main__':
    main()
