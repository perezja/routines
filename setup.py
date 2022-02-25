#!/usr/bin/env python
# encoding: utf-8

import os
import sys
from collections import namedtuple
from setuptools import setup, find_packages

if sys.version_info < (3, 8):
    raise SystemExit("Python 3.8 or later is required.")

level_map = {'plan': '.dev'}

version_info = namedtuple('version_info', ('major', 'minor', 'micro', 'releaselevel', 'serial')) \
		(0, 0, 0, 'plan', 0)

version = ".".join([str(i) for i in version_info[:3]]) + \
		((level_map.get(version_info.releaselevel, version_info.releaselevel[0]) + \
		str(version_info.serial)) if version_info.releaselevel != 'final' else '')  

author = namedtuple('Author', ['name', 'email'])("James A. Perez", 'perezja@wustl.edu')

description = "Distributed workflow execution"
url = 'https://github.com/perezja/routines/'

#version = description = url = author = version_info = ''
#exec(open(os.path.join("routines", "release.py")).read()) 

here = os.path.abspath(os.path.dirname(__file__))

trove_map = {
    'plan': "Development Status :: 1 - Planning",
    'alpha': "Development Status :: 3 - Alpha",
    'beta': "Development Status :: 4 - Beta",
    'final': "Development Status :: 5 - Production/Stable",
}

# Entry Point

setup(
    name = "routines",
    version = version,
    packages = find_packages(),
    description = description,
    entry_points = {
        'console_scripts': [
            'routines = routines.client:main',
        ],
    },
)
