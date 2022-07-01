"""

HttpCtrl library provides HTTP/HTTPS client and server API to Robot Framework to make REST API testing easy.

Authors: Andrei Novikov
Date: 2018-2022
Copyright: The 3-Clause BSD License

"""

import os

from setuptools import setup


def load_readme():
    readme_file = 'PKG-INFO.rst'
    if os.path.isfile(readme_file):
        with open(readme_file) as file_descr:
            return file_descr.read()

    return "robotframework-httpctrl is a library for Robot Framework that provides HTTP/HTTPS client and HTTP server services."


def load_version():
    version_file = 'VERSION'
    if os.path.isfile(version_file):
        with open(version_file) as file_descr:
            return file_descr.read()
    
    return 'unknown'


setup(
    name='robotframework-httpctrl',
    packages=['HttpCtrl', 'HttpCtrl.utils'],
    version=load_version(),
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
    license='BSD-3-Clause',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: BSD License',
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

    python_requires='>=3.8',
    install_requires=['robotframework'],

    package_dir={'': 'src'},
    data_files=[('', ['LICENSE', 'CHANGES', 'README.rst', 'PKG-INFO.rst', 'VERSION'])]
)

