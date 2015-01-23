# coding=utf-8
from __future__ import unicode_literals
from setuptools import setup, find_packages

VERSION = "0.1.0"

with open('requirements/base.txt') as f:
    requirements = f.readlines()

setup(
    name="django-doc-brown",
    version=VERSION,
    author="Víðir Valberg Guðmundsson",
    author_email="valberg@orn.li",
    description="Version control for Django models",
    keywords="django version revision vcs",
    packages=find_packages(),
    zip_safe=False,
    install_requires=[r.strip() for r in requirements],
    include_package_data=True,
)
