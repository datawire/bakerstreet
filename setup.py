from setuptools import setup

metadata = {}
with open("bakerstreet/_metadata.py") as metadata_file:
    exec(metadata_file.read(), metadata)

setup(name='datawire-bakerstreet',
      version=metadata["__version__"],
      description=metadata["__summary__"],
      author=metadata["__author__"],
      author_email=metadata["__email__"],
      url=metadata["__uri__"],
      license=metadata["__license__"],
      packages=['bakerstreet'],
      install_requires=[],
      entry_points={"console_scripts": [
          "sherlock = bakerstreet.sherlock:call_main"
          "watson = bakerstreet.watson:call_main"
      ]})
