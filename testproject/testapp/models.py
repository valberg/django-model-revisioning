from django.db import models

from model_revisioning.fields import RevisionedForeignKey
from model_revisioning.models import RevisionModel


class NonRevisionedModel(models.Model):
    char = models.CharField(max_length=255, null=True, blank=True)


class Baz(RevisionModel):
    char = models.CharField(max_length=255, null=True, blank=True)
    int = models.IntegerField(null=True, blank=True)
    text = models.TextField(null=True, blank=True)

    class Revisions:
        fields = ["char", "text"]


class Bar(RevisionModel):
    char = models.CharField(max_length=255, null=True, blank=True)
    int = models.IntegerField(null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    boolean = models.BooleanField(default=False)
    null_boolean = models.NullBooleanField()

    hello_world = models.CharField(max_length=255, null=True, blank=True)

    non_revisioned_foreign_key = models.ForeignKey(
        NonRevisionedModel, null=True, blank=True, on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(
        "auth.User", null=True, blank=True, on_delete=models.CASCADE
    )
    groups = models.ForeignKey(
        "auth.Group", null=True, blank=True, on_delete=models.CASCADE
    )

    parent_bar = RevisionedForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE
    )


class ModelWithRevisionedForeignKey(RevisionModel):

    foo = RevisionedForeignKey(
        "testapp.ModelOnOtherEndOfRevisionedForeignKey",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )


class ModelOnOtherEndOfRevisionedForeignKey(RevisionModel):
    char = models.CharField(max_length=255)


class ModelWithUniqueField(RevisionModel):
    unique_field = models.CharField(max_length=10, unique=True)


class ModelWithDatabaseConstraint(RevisionModel):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("choice", "foo"), name="one_choice_per_foo")
        ]

    choice = models.CharField(max_length=10, choices=[("one", "One"), ("two", "Two")])

    foo = RevisionedForeignKey(
        "testapp.ModelOnOtherEndOfRevisionedForeignKey", on_delete=models.CASCADE
    )


class SoftDeleted(RevisionModel):
    content = models.TextField()

    class Revisions:
        soft_deletion = True


class ModelWithoutOptions(RevisionModel):
    content = models.TextField()


class StringRelatedModel(RevisionModel):
    char = models.CharField(max_length=255, null=True, blank=True)
