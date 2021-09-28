"""

HttpCtrl library provides HTTP/HTTPS client and server API to Robot Framework to make REST API testing easy.

Authors: Andrei Novikov
Date: 2018-2019
Copyright: GNU Public License

HttpCtrl is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

HttpCtrl is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import os

from setuptools import setup
from setuptools import find_packages


def load_readme():
    readme_file = 'PKG-INFO.rst'
    if os.path.isfile(readme_file):
        with open(readme_file) as file_descr:
            return file_descr.read()

    return "robotframework-httpctrl is a library for Robot Framework that provides HTTP/HTTPS client and HTTP server services."


setup(
    name='robotframework-httpctrl',
    packages=['HttpCtrl', 'HttpCtrl.utils'],
    version='0.1.8',
    description='robotframework-httpctrl is a library for Robot Framework that provides HTTP/HTTPS client and HTTP server services',
    platforms='any',
    long_description=load_readme(),
    url='https://github.com/annoviko/robotframework-httpctrl',
    project_urls={
        'Homepage': 'https://annoviko.github.io/robotframework-httpctrl/',
        'Repository': 'https://github.com/annoviko/robotframework-httpctrl',
        'Documentation': 'https://annoviko.github.io/robotframework-httpctrl/',
        'Bug Tracker': 'https://github.com/annoviko/robotframework-httpctrl/issues'
    },
    license='GNU Public License',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Education',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: Software Development :: Testing',
        'Framework :: Robot Framework :: Library'
    ],
    keywords='httpctrl http https robotframework client server json test testing',
    author='Andrei Novikov',
    author_email='spb.andr@yandex.ru',

    python_requires='>=3.4',
    install_requires=['robotframework'],

    package_dir={'': 'src'}
)

