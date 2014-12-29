# coding: utf-8
from contextlib import contextmanager

from testapp import models

import pytest
import loremipsum


def test_revision_on_edit(db):
    foo1 = models.Foo.objects.create()
    assert foo1.revision_set.count() == 0

    foo1.char = 'Foo1'
    foo1.save()

    assert foo1.revision_set.count() == 1

    revision1 = foo1.revision_set.first()
    assert revision1.char is None

    text_body = loremipsum.generate_paragraph()
    foo1.char = 'Foo1 updated'
    foo1.text = text_body
    foo1.save()

    assert foo1.revision_set.count() == 2

    revision2 = revision1.get_next_in_order()
    assert revision2.text is None

    foo1.save()
    foo1.save()
    foo1.save()

    assert foo1.revision_set.count() == 2
