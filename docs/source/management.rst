Management commands
===================


graph_revision
--------------

``./manage.py graph_revision <model_path:label> <pk> <output>``

Create a graphviz directed graph of revisions. Useful for getting visual
overview of branches.

Two files will be produced. A ``.gv`` with the raw graphviz markup, and a
``.gv.png`` which is a rendered image.

**Requirements:**

Both `graphviz <http://www.graphviz.org/>`_ itself, and the python package called
`graphviz <https://pypi.python.org/pypi/graphviz/>`_ are required.

**Arguments:**

``model_path``
    Dotted path to model, skipping ``models``. Thus a model named
    ``Bar`` in the app ``foo`` would be ``foo.Bar``.

    By default the ``pk`` of the revision is used as a label for the
    corresponding node. If another field should be used, append it prefixed with
    a ``:``. Thus to show the field ``name`` use: ``foo.Bar:name``.

``pk``
    Which instance of the given model to graph.

``output``
    Name of the output file.

**Example**

``./manage.py graph_revision foo.Bar:name 42 graph``
