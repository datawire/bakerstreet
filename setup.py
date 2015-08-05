from setuptools import setup

metadata = {}
with open("_metadata.py") as fp:
    exec(fp.read(), metadata)

setup(name='bakerstreet',
      version=metadata["__version__"],
      description=metadata["__summary__"],
      author=metadata["__author__"],
      author_email=metadata["__email__"],
      url=metadata["__uri__"],
      license=metadata["__license__"],
      install_requires=['datawire-common'],
      scripts=['sherlock', 'watson'])
