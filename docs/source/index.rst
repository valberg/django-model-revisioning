Welcome to the django-model-history documentation!
==================================================

django-model-history adds history to your models - migration compatible!

Contents:

.. toctree::
   :maxdepth: 2

   options
   admin
   signals

What does django-model-history provide?
---------------------------------------

django-model-history makes copies of your models so that the django migration framework actual tables in your database.

Say you have a model called `Movie`, django-model-history will create a model called `MovieRevision`.
Every time you save an instance of `Movie` a `MovieRevision` instance will be created as well.

If you then add new fields to `Movie`, django-model-history will pick up on it and add the same fields to `MovieRevision`.

Installation
------------

Currently django-model-history has not been released to PyPI.

You can install the development version using the following command::

    pip install git+https://github.com/valberg/django-model-history@master#egg=django-model-history


Usage
-----

To install a flux capacitor in your model inherit from ``RevisionModel``
and define a ``Revisions`` class in your model, like this::

    from django.db import models
    from model_history.models import RevisionModel

    class Movie(RevisionModel):
        name = models.CharField(max_length=200)
        year = models.IntegerField()

        class Revisions:
            fields = ["name", "year"]


See :doc:`options` for which options are available.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
