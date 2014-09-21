
import os
from setuptools import setup
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
    'Natural Language :: English',
    'Topic :: Software Development :: Libraries :: Python Modules'
]

setup(
    name='qt4reactor',
    version='1.6.dev.1',
    license='MIT',
    classifiers=classifiers,
    author='Glenn H. Tarbox',
    author_email='glenn@tarbox.org',
    description='Twisted Qt Integration',
    long_description=read('README.rst'),
    url='https://github.com/ghtdak/qtreactor',
    download_url='https://github.com/ghtdak/qtreactor/tarball/master/#egg-qt4reactor.1.6.dev.1',
    dependency_links=['https://github.com/ghtdak/qtreactor/tarball/master/#egg-qt4reactor.1.6.dev.1'],
    scripts=glob("./bin/*"),
    py_modules=['qtreactor'],
    keywords=['Qt', 'twisted'],
    install_requires=['twisted']
)
