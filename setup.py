from setuptools import setup, find_packages

VERSION = "0.1.0"

with open('requirements/base.txt') as f:
    requirements = f.readlines()

setup(
    name="django-model-history",
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
