Options
=======

Doc Brown uses a class similar to the ``Meta`` class in django models. Listed
below are all the options available.


``soft_deletion``
-----------------
Controls whether instances actually get deleted or not when ``delete()`` is
called. If set to ``True`` a ``is_deleted`` boolean field will be added to the
model and this set instead of deleting the instance.
