Signals
=======

Django Model History emits the following signals when dealing with revisions:


pre_revision
------------

.. data:: model_revisioning.signals.pre_save
   :module:

Sent before creating a revision.

Arguments:

``sender``
    The model class.

``instance``
    The instance for which a revision is about to be created.


post_revision
-------------

.. data:: model_revisioning.signals.post_save
   :module:

Sent a revision has been created.

Arguments:

``sender``
    The model class.

``instance``
    The instance for which a revision has been created.

``revision``
    The revision instance itself.


pre_change_head
---------------

.. data:: model_revisioning.signals.pre_change_head
   :module:

Sent before head gets changed on an object.

Arguments:

``sender``
    The model class.

``instance``
    The instance for which the head is about to change

``current_head``
    The current head.

``future_head``
    The head which is about to become the current.


post_change_head
----------------

.. data:: model_revisioning.signals.post_change_head
   :module:

Sent after head gets changed on an object.

Arguments:

``sender``
    The model class.

``instance``
    The instance for which the head is about to change

``old_head``
    The head which used to be current.

``new_head``
    The head which is now current.
