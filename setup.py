#!/usr/bin/env python
import os
from setuptools import setup, find_packages
from glob import glob

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: X11 Applications :: Qt',
    'Framework :: Twisted',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Natural Language :: English',
    'Topic :: Software Development :: Libraries :: Python Modules'
]

setup(
    name='qt4reactor',
    version='1.5',
    license='MIT',
    classifiers=classifiers,
    author='Glenn H. Tarbox',
    author_email='glenn@tarbox.org',
    description='Twisted Qt Integration',
    long_description=read('README.rst'),
    url='https://github.com/ghtdak/qtreactor',
    scripts=glob("./bin/*"),
    packages=find_packages(),
    py_modules=['qt4reactor'],
    keywords=['Qt', 'twisted'],
    install_requires=['twisted']
)
