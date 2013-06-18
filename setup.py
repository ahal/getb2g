# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from setuptools import setup, find_packages
import os
import sys

PACKAGE_NAME = "getb2g"
PACKAGE_VERSION = "2.11"

desc = """Get the latest B2G nightly builds for a specific device"""
deps = ['BeautifulSoup4',
        'mozinfo',
        'mozinstall',
        'mozlog',
        'mozfile>=0.9',]
# take description from README
here = os.path.dirname(os.path.abspath(__file__))
try:
    description = file(os.path.join(here, 'README.md')).read()
except IOError, OSError:
    description = ''

setup(name=PACKAGE_NAME,
      version=PACKAGE_VERSION,
      description=desc,
      long_description=description,
      author='Andrew Halberstadt, Mozilla',
      author_email='halbersa@gmail.com',
      url='http://github.com/ahal/getb2g',
      license='MPL 1.1/GPL 2.0/LGPL 2.1',
      packages=find_packages(exclude=['legacy']),
      zip_safe=False,
      install_requires=deps,
      entry_points="""
      [console_scripts]
      getb2g = getb2g:cli
      """,
      platforms =['Any'],
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
                   'Operating System :: OS Independent',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                  ]
     )
