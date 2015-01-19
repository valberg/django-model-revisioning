# coding: utf-8
from contextlib import contextmanager

from testapp import models

import pytest


def test_revision_on_edit(db):
    bar1 = models.Bar.objects.create()
    assert bar1.id
    assert bar1.revision_class.objects.count() == 1

    bar1.char = 'Bar1'
    bar1.save()
    assert bar1.revision_class.objects.count() == 2

    text_body = 'lalala'
    bar1.char = 'Bar1 updated'
    bar1.text = text_body
    bar1.save()

    assert bar1.revision_class.objects.count() == 3

    revision2 = bar1.revision_class.objects.last()
    assert revision2.text == text_body


def test_foreign_keys(db):
    non_revisioned_instance = models.NonRevisionedModel.objects.create()
    bar1 = models.Bar.objects.create(
        non_revisioned_foreign_key=non_revisioned_instance
    )
    assert bar1.revision_class.objects.count() == 1

    bar1.non_revisioned_foreign_key = None
    bar1.save()
    assert bar1.revision_class.objects.count() == 2

    revision1 = bar1.revision_class.objects.first()
    assert revision1.non_revisioned_foreign_key == non_revisioned_instance

    non_revisioned_instance.delete()

    assert bar1.revision_class.objects.count() == 2


def test_parent_revision(db):
    bar1 = models.Bar.objects.create()

    first_revision = bar1.current_revision
    assert first_revision.parent_revision is None

    bar1.char = 'foo'
    bar1.save()

    assert bar1.current_revision != first_revision
    assert bar1.current_revision.parent_revision == first_revision


def test_change_head(db):
    bar1 = models.Bar.objects.create()

    first_revision = bar1.revisions.get()

    bar1.char = 'foo'
    bar1.save()

    assert bar1.char == 'foo'

    bar1.set_head_to(first_revision)

    assert bar1.char is None
    assert first_revision.is_head


def test_branching(db):
    bar1 = models.Bar.objects.create()
    first_revision = bar1.revisions.get()

    bar1.char = 'foo'
    bar1.save()

    bar1.set_head_to(first_revision)

    bar1.char = 'baz'
    bar1.save()

    assert bar1.revisions.filter(parent_revision=first_revision).count() == 2


def test_specific_fields_option(db):
    baz1 = models.Baz.objects.create()
    first_revision = baz1.revisions.get()
    assert not hasattr(first_revision, 'int')


def test_specific_fields_option_change_head(db):
    baz1 = models.Baz.objects.create()

    first_revision = baz1.revisions.get()

    baz1.char = 'foo'
    baz1.save()

    assert baz1.char == 'foo'

    baz1.set_head_to(first_revision)

    assert baz1.char is None
    assert first_revision.is_head


def test_soft_deletion(db):
    soft_deleted1 = models.SoftDeleted.objects.create()
    soft_deleted1.delete()
    assert soft_deleted1.is_deleted is True

    # Bar objects should delete!
    bar1 = models.Bar.objects.create()
    bar1.delete()
    assert bar1.id is None


def test_model_without_options(db):
    without_options = models.ModelWithoutOptions()
    assert without_options._revisions.fields == ['content']
    assert without_options._revisions.soft_deletion is False
