.. Django Doc Brown documentation master file, created by
   sphinx-quickstart on Sun Jan 11 14:18:51 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Django Doc Brown's documentation!
============================================

Doc Brown is here to install a flux capacitor in you django models. From hereon
you will never loose any data - you can just travel in time!

Contents:

.. toctree::
   :maxdepth: 2

   options
   revision_types


Installation
------------

Install from pip::

    pip install djang-doc-brown


Usage
-----

To install a flux capacitor in your model inherit from ``RevisionModel``
and define a ``Revisions`` class in your model, like this::

    from django.db import models
    from doc_brown.models import RevisionModel

    class MyModel(RevisionModel):
        name = models.TextField()

        class Revisions:
            fields = ['name']
            soft_deletion = True


See :doc:`options` for which options are available.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

