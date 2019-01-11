# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os
from harvest_explorer.cli import VERSION


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


try:
    with open('requirements.txt') as f:
        required = f.read().splitlines()
except:
    print('some error reading the requirements.txt file')
    import sys
    sys.exit(1)

setup(name="harvest-explorer",
      author="Jorge Sanz",
      author_email="jsanz@carto.com",
      description="An app to migrate Harvest tasks",
      long_description=read('README.md'),
      long_description_content_type="text/markdown",
      keywords="harvest api",
      license="BSD",
      classifiers=[
          "License :: OSI Approved :: BSD License",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.7",
      ],
      version=VERSION,
      url="https://github.com/CartoDB/TBD",
      install_requires=required,
      packages=find_packages(),
      include_package_data=True,
      entry_points='''
[console_scripts]
harvest-explorer=harvest_explorer.cli:cli
      '''
      )
