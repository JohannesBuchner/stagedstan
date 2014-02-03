#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except:
    from distutils.core import setup

long_description = None
with open('README.rst') as file:
    long_description = file.read()

setup(
    name = "stagedstan",
    version = "0.1",
    description = "Cached execution for the Stan Hamiltonean Monte Carlo",
    author = "Johannes Buchner",
    author_email = "johannes.buchner.acad [@t] gmx.com",
    maintainer = "Johannes Buchner",
    maintainer_email = "johannes.buchner.acad [@t] gmx.com",
    url = "http://github.com/JohannesBuchner/stagedstan",
    license = "GPLv3",
    packages = ["stagedstan"],
    requires = ["numpy (>=1.5)", ],
    long_description=long_description,
)

