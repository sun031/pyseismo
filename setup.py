from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name = 'swseismo',
    version = '0.0.1',
    keywords = ('seismology', 'test'),
    description = 'my seismological modules',
    license = 'GPL License',

    author = 'Weijia Sun',
    author_email = 'swj@mail.iggcas.ac.cn',

    packages = find_packages(),
    platforms = 'any',
)