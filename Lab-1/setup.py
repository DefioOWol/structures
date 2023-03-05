"""Модуль установки."""
from setuptools import Extension, setup


setup(ext_modules=[Extension('carray', ['carray.c']),
                   Extension('binary_search', ['binary_search.c'])])
