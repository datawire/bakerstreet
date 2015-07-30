from setuptools import setup

__version__ = '0.4'

setup(name='bakerstreet',
      version=__version__,
      description='Service discovery for microservices',
      author='datawire.io',
      author_email='hello@datawire.io',
      license='Apache License Version 2.0',
      url='http://www.datawire.io',
      install_requires=['datawire-common'],
      scripts=['sherlock', 'watson'])
