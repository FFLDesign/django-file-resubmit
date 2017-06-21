#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (c) 2011 Ilya Shalyapin
#
#  django-file-resubmit is free software under terms of the MIT License.
#

import os
from setuptools import setup, find_packages

setup(
    name     = 'django-file-resubmit',
    packages = find_packages(),
    package_data = {'': ['static/*/*/*']},
    requires = ['python (>= 2.7)', 'django (>= 1.5)'],
    description  = 'Keeps submitted files when validation errors occur.',
    author       = 'Ilya Shalyapin and others',
    # TODO: Don't merge these into master branch.
    version  = '6.6.6',
    author_email = 'derick@ffldesign.com',
    url          = 'https://github.com/FFLDesign/django-file-resubmit/tree/ffldesign',
    download_url = 'https://github.com/FFLDesign/django-file-resubmit/archive/ffldesign.zip',
    license      = 'MIT License',
    keywords     = 'django form filefield resubmit',
    classifiers  = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
)
