from distutils.core import setup

setup(name='bakerstreet',
      version='0.4',
      description='Service discovery for microservices',
      author='datawire.io',
      author_email='hello@datawire.io',
      license='Apache License Version 2.0',
      url='http://www.datawire.io',
      install_requires=['datawire-common'],
      scripts=['sherlock', 'watson'])
