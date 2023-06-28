# from distutils.core import setup
import os
# from robin_ai import __version__
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

__version__ = 0.5

setup(
  install_requires=required,
  name='robin_ai',
  # py_modules=['robin_ai', 'ai_core2'],
  version=__version__,
  author='Roman Kozak',
  author_email='cossack.roman@gmail.com',
  # packages=['robin_ai'],
  packages=find_packages(),
  url='https://github.com/phoenixway/robin_assistant',
  license='MIT',
  provides=['robin_ai'],
  description='Robin AI assistant.'
  # long_description=open('README.md').read(),
  #scripts=['robin_ai.py']
)
