Welcome to the django-model-revisioning documentation!
======================================================

django-model-revisioning adds history to your models - migration compatible!

Contents:

.. toctree::
   :maxdepth: 2

   options
   admin
   signals
   management

What does django-model-revisioning provide?
-------------------------------------------

django-model-revisioning makes copies of your models so that the django migration framework actual tables in your database.

Say you have a model called `Movie`, django-model-revisioning will create a model called `MovieRevision`.
Every time you save an instance of `Movie` a `MovieRevision` instance will be created as well.

If you then add new fields to `Movie`, django-model-revisioning will pick up on it and add the same fields to `MovieRevision`.

Installation
------------

You can install the pre-release version using the following command::

    pip install django-model-revisioning>=0.0.1-alpha

Note that this is an alpha version and is not recommended for production use!

Usage
-----

To install a flux capacitor in your model inherit from ``RevisionModel``
and define a ``Revisions`` class in your model, like this::

    from django.db import models
    from model_revisioning.models import RevisionModel

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
