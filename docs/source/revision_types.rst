Revision Types
==============

Doc Brown knows different ways of traveling in time. Here we list these
different ways.


Single table
------------
A fairly simple approach where there only exists a single table in the database.
The model is augmented with a ``is_revision`` boolean field and a self-referring
``revision_for`` foreign key.

This approach is based on having a manager to distinguish between revisions and
current instances.

Usage::

    class Revisions:
        revision_type = 'single'


Double table
------------
A more "magical" approach where a additional table is created copying fields
from the model and an additional ``revision_for`` field referring back to the
original model.

This has the benefit of keeping the main table clean of revisions, avoids having
unused columns for current instances, and the revisioning can be selective of
which fields to actually revision. The downside is that the code for this is
quite more complex.

Usage::

    class Revisions:
        revision_type = 'double'
