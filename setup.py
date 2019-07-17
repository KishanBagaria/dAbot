#!/usr/bin/env python
# coding: utf-8
from setuptools import setup

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

setup(
  name='dAbot',
  version='2019.07.18',
  description='CLI tool to automate stuff on DeviantArt.com',
  url='https://github.com/KishanBagaria/dAbot',
  author='Kishan Bagaria',
  author_email='hi@kishan.info',
  license='MIT',
  classifiers=[
    'Development Status :: 3 - Alpha',

    'Environment :: Console',

    'License :: OSI Approved :: MIT License',

    'Programming Language :: Python :: 2.7',
  ],
  keywords=['deviantart', 'llama', 'bot'],
  packages=['dAbot'],
  install_requires=['colorama', 'docopt', 'requests', 'retrying', 'PyYAML', 'python-dateutil'],
  download_url='https://codeload.github.com/KishanBagaria/dAbot/tar.gz/master',
  entry_points={
    'console_scripts': ['dAbot=dAbot.dAbot:main'],
  }
)
