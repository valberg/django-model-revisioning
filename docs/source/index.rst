Welcome to Django Model History documentation!
============================================

Django Model History adds history to your models - migration compatible!

Contents:

.. toctree::
   :maxdepth: 2

   options
   admin
   signals
   management
   api

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
    from model_history.fields import RevisionedForeignKey

    class MyModel(RevisionModel):
        name = models.TextField()

        class Revisions:
            fields = ['name']


    class OtherModel(RevisionedModel):
        my_model = RevisionedForeignKey('MyModel')

See :doc:`options` for which options are available.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
