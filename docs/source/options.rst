Options
=======

Doc Brown uses a class similar to the ``Meta`` class in django models. Listed
below are all the options available.


``soft_deletion``
-----------------
Controls whether instances actually get deleted or not when ``delete()`` is
called. If set to ``True`` a ``is_deleted`` boolean field will be added to the
model and this set instead of deleting the instance.


``revision_type``
-----------------
Which type of revision method to use. See :doc:`revision_types` for more detail.


``fields``
----------
A list of which fields to revision. Only has effect when using the ``double``
revision type.
