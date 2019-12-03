import pytest
from testapp import models


def test_revision_on_edit(db):
    bar1 = models.Bar.objects.create()
    assert bar1.id
    assert bar1.revisions.count() == 1

    bar1.char = "Bar1"
    bar1.save()
    assert bar1.revisions.count() == 2

    text_body = "Integer posuere erat a ante venenatis dapibus posuere velit aliquet."

    bar1.char = "Bar1 updated"
    bar1.text = text_body
    bar1.save()

    assert bar1.revisions.count() == 3

    revision2 = bar1.revisions.last()
    assert revision2.text == text_body


def test_non_revisioned_foreign_keys(db):
    non_revisioned_instance = models.NonRevisionedModel.objects.create()

    bar = models.Bar.objects.create(non_revisioned_foreign_key=non_revisioned_instance)

    assert bar.revisions.last().non_revisioned_foreign_key == non_revisioned_instance

    bar.save()

    assert bar.revisions.last().non_revisioned_foreign_key == non_revisioned_instance


def test_parent_revision(db):
    bar1 = models.Bar.objects.create()

    first_revision = bar1.current_revision
    assert first_revision.parent_revision is None

    bar1.char = "foo"
    bar1.save()

    assert bar1.current_revision != first_revision
    assert bar1.current_revision.parent_revision == first_revision


def test_change_head(db):
    bar1 = models.Bar.objects.create()

    first_revision = bar1.revisions.get()

    bar1.char = "foo"
    bar1.save()

    assert bar1.char == "foo"

    bar1.set_head(first_revision)

    assert bar1.char is None
    assert first_revision.is_head


def test_branching(db):
    bar1 = models.Bar.objects.create()
    first_revision = bar1.revisions.get()

    bar1.char = "foo"
    bar1.save()

    bar1.set_head(first_revision)

    bar1.char = "baz"
    bar1.save()

    assert bar1.revisions.filter(parent_revision=first_revision).count() == 2


def test_specific_fields_option(db):
    baz1 = models.Baz.objects.create()
    first_revision = baz1.revisions.get()
    assert not hasattr(first_revision, "int")


def test_specific_fields_option_change_head(db):
    baz1 = models.Baz.objects.create()

    first_revision = baz1.revisions.get()

    baz1.char = "foo"
    baz1.save()

    assert baz1.char == "foo"

    baz1.set_head(first_revision)

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
    assert without_options._revisions.fields == ["content"]
    assert without_options._revisions.soft_deletion is False


def test_revision_on_update(db):
    bar1 = models.Bar.objects.create()
    bar2 = models.Bar.objects.create()

    models.Bar.objects.all().update(char="foo")

    assert bar1.revisions.count() == 2
    assert bar2.revisions.count() == 2

    assert bar1.revisions.filter(char="foo").count() == 1
    assert bar2.revisions.filter(char="foo").count() == 1


def test_revision_model_admin_raises_exception_on_non_revision_model(db):
    from django.contrib import admin
    from model_revisioning.admin import RevisionModelAdmin
    from django.core.exceptions import ImproperlyConfigured

    with pytest.raises(ImproperlyConfigured):
        if admin.site.is_registered(models.NonRevisionedModel):
            admin.site.unregister(models.NonRevisionedModel)

        admin.site.register(models.NonRevisionedModel, RevisionModelAdmin)


def test_foreignkey_to_same_model(db):
    bar1 = models.Bar.objects.create(char="#" * 20)
    bar2 = models.Bar.objects.create(char="*" * 10, parent_bar=bar1)

    bar3 = models.Bar.objects.create()
    bar2.parent_bar = bar3
    bar2.save()

    bar2.parent_bar = None
    bar2.save()

    assert bar2.revisions.all()[0].parent_bar == bar1.current_revision
    assert bar2.revisions.all()[1].parent_bar == bar3.current_revision
    assert bar2.revisions.all()[2].parent_bar is None


def test_foreignkey_to_same_object(db):

    bar = models.Bar.objects.create(char="hest")

    first_revision = bar.current_revision

    bar.parent_bar = bar
    bar.save()

    second_revision = bar.current_revision

    assert first_revision.parent_bar is None
    assert second_revision.parent_bar == second_revision


def test_foreignkey_to_other_revisioned_model(db):
    foo = models.ModelOnOtherEndOfRevisionedForeignKey.objects.create(char="foo")
    bar = models.ModelWithRevisionedForeignKey.objects.create()

    bar.foo = foo
    bar.save()
    assert bar.current_revision.foo == foo.current_revision
    assert bar.revisions.count() == 2


def test_new_revision_when_related_model_is_edited(db):
    # Triggers new foo revision (1 revision)
    foo = models.ModelOnOtherEndOfRevisionedForeignKey.objects.create(char="foo")

    # Triggers new bar revision (1 revision)
    bar = models.ModelWithRevisionedForeignKey.objects.create(foo=foo)

    foo.char = "trigger revision"

    # Triggers new bar revision (2 revisions)
    # Triggers new foo revision (2 revisions)
    foo.save()

    assert bar.revisions.count() == 2
    assert foo.revisions.count() == 2

    # Triggers new bar1 revision (1 revision)
    bar1 = models.ModelWithRevisionedForeignKey.objects.create(foo=foo)

    foo.char = "trigger revision again"

    # Triggers new bar revision (3 revisions) and bar1 revision (2 revisions)
    # Triggers new foo revision (3 revisions)
    foo.save()

    assert bar.revisions.count() == 3
    assert bar1.revisions.count() == 2
    assert foo.revisions.count() == 3


def test_making_revision_head_cascades_to_foreign_keys(db):
    foo = models.ModelOnOtherEndOfRevisionedForeignKey.objects.create(char="foo")

    # Triggers new bar revision (1 revision)
    bar = models.ModelWithRevisionedForeignKey.objects.create(foo=foo)

    foo.char = "trigger revision"

    # Triggers new bar revision (2 revisions)
    foo.save()

    bar.refresh_from_db()

    bar.set_head(bar.revisions.first())

    bar.refresh_from_db()

    foo.refresh_from_db()

    assert foo.char == "foo"


def test_uniqueness_is_removed_from_revisions(db):
    foo = models.ModelWithUniqueField.objects.create(unique_field="test")

    foo.unique_field = "test1"
    foo.save()

    # If uniqueness is not removed the following will fail with IntegrityError
    foo.unique_field = "test"
    foo.save()


def test_note_on_revision(db):
    foo = models.ModelOnOtherEndOfRevisionedForeignKey.objects.create(char="foo")
    bar = models.ModelWithRevisionedForeignKey.objects.create(foo=foo)
    foo.char = "trigger revision"
    foo.save()
    assert (
        bar.current_revision.note.lower()
        == f"created since {foo._meta.model_name} (pk: {foo.pk}) changed."
    )
