from setuptools import setup, find_packages
__version__ = "0.5.0"


setup(name='client4robin',
      version=__version__,
      author='Roman Kozak',
      scripts=['ws-client-cli.py'],
      author_email='cossack.roman@gmail.com',
      packages=find_packages(),
      url='https://github.com/phoenixway/robin_assistant',
      license='MIT',
      description='Robin AI assistant.'
      )
