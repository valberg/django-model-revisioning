from django.db import models

from model_history.fields import RevisionedForeignKey
from model_history.fields import RevisionedManyToManyField
from model_history.models import RevisionModel


class NonRevisionedModel(models.Model):
    char = models.CharField(max_length=255, null=True, blank=True)


class Baz(RevisionModel):
    char = models.CharField(max_length=255, null=True, blank=True)
    int = models.IntegerField(null=True, blank=True)
    text = models.TextField(null=True, blank=True)

    class Revisions:
        fields = ["char", "text"]


class Foo(RevisionModel):
    char = models.CharField(max_length=255, null=True, blank=True)


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

    foo = RevisionedForeignKey(
        "testapp.Foo", null=True, blank=True, on_delete=models.CASCADE
    )

    many_baz = RevisionedManyToManyField(
        "testapp.Baz", through="testapp.BarManyBazRelation"
    )

    class Revisions:
        fields = "__all__"


class BarManyBazRelation(RevisionModel):
    bar = RevisionedForeignKey("testapp.Bar", on_delete=models.CASCADE)
    baz = RevisionedForeignKey("testapp.Baz", on_delete=models.CASCADE)


class SoftDeleted(RevisionModel):
    content = models.TextField()

    class Revisions:
        soft_deletion = True


class ModelWithoutOptions(RevisionModel):
    content = models.TextField()


class StringRelatedModel(RevisionModel):
    char = models.CharField(max_length=255, null=True, blank=True)
