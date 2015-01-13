# coding: utf-8
from contextlib import contextmanager

from testapp import models

import pytest
import loremipsum


def test_revision_on_edit(db):
    bar1 = models.Bar.objects.create()
    assert bar1.revision_class.objects.count() == 0

    bar1.char = 'Bar1'
    bar1.save()

    assert bar1.revision_class.objects.count() == 1

    revision1 = bar1.revision_class.objects.last()
    assert revision1.char is None

    text_body = loremipsum.generate_paragraph()
    bar1.char = 'Bar1 updated'
    bar1.text = text_body
    bar1.save()

    assert bar1.revision_class.objects.count() == 2

    revision2 = bar1.revision_class.objects.last()
    assert revision2.text is None

    # bar1.save()
    # bar1.save()
    # bar1.save()

    assert bar1.revision_class.objects.count() == 2


def test_foreign_keys(db):
    non_revisioned_instance = models.NonRevisionedModel.objects.create()
    bar1 = models.Bar.objects.create(
        non_revisioned_foreign_key=non_revisioned_instance
    )
    assert bar1.revision_class.objects.count() == 0

    bar1.non_revisioned_foreign_key = None
    bar1.save()
    assert bar1.revision_class.objects.count() == 1

    revision1 = bar1.revision_class.objects.first()
    assert revision1.non_revisioned_foreign_key == non_revisioned_instance

    non_revisioned_instance.delete()

    assert bar1.revision_class.objects.count() == 1
