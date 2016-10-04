# -*- coding: utf-8 -*-
"""Setup file for the EasyDjango project.
"""

import codecs
import os.path
import re

import sys
from setuptools import setup, find_packages

# avoid a from easydjango import __version__ as version (that compiles easydjango.__init__
#   and is not compatible with bdist_deb)
version = None
for line in codecs.open(os.path.join('easydjango', '__init__.py'), 'r', encoding='utf-8'):
    matcher = re.match(r"""^__version__\s*=\s*['"](.*)['"]\s*$""", line)
    version = version or matcher and matcher.group(1)
python_version = (sys.version_info[0], sys.version_info[1])

# get README content from README.md file
with codecs.open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as fd:
    long_description = fd.read()


extras_requirements = {}
install_requirements = ['django', 'celery', 'gunicorn', 'django-bootstrap3']
if python_version < (3, 3):
    install_requirements.append('funcsigs')

entry_points = {'console_scripts': [
    'easydjango-ctl = easydjango.scripts:control',
    'easydjango-celery = easydjango.scripts:celery',
    'easydjango-django = easydjango.scripts:django',
    'easydjango-uwsgi = easydjango.scripts:uwsgi',
    'easydjango-gunicorn = easydjango.scripts:gunicorn',
                                     ]}
extras_requirements['deb'] = ['stdeb>=0.8.5']
extras_requirements['pipeline'] = ['django-pipeline']
extras_requirements['debug'] = ['django-debug-toolbar']

setup(
    name='easydjango',
    version=version,
    description='No description yet.',
    long_description=long_description,
    author='Matthieu Gallet',
    author_email='github@19pouces.net',
    license='CeCILL-B',
    url='',
    entry_points=entry_points,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='easydjango.tests',
    install_requires=install_requirements,
    extras_require=extras_requirements,
    setup_requires=[],
    classifiers=['Development Status :: 3 - Alpha', 'Operating System :: MacOS :: MacOS X',
                 'Operating System :: Microsoft :: Windows', 'Operating System :: POSIX :: BSD',
                 'Operating System :: POSIX :: Linux', 'Operating System :: Unix',
                 'License :: OSI Approved :: CEA CNRS Inria Logiciel Libre License, version 2.1 (CeCILL-2.1)',
                 'Programming Language :: Python :: 2.6', 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.4', 'Programming Language :: Python :: 3.5'],
)
