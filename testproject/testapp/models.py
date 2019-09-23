from django.db import models

from model_history.models import RevisionModel


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

    # TODO: Get this to work:
    parent_bar = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE
    )

    baz = models.ForeignKey(Baz, null=True, blank=True, on_delete=models.CASCADE)

    class Revisions:
        fields = "__all__"


class SoftDeleted(RevisionModel):
    content = models.TextField()

    class Revisions:
        soft_deletion = True


class ModelWithoutOptions(RevisionModel):
    content = models.TextField()


class SerializedRelatedModel(RevisionModel):
    non_revisioned_foreign_key = models.ForeignKey(
        NonRevisionedModel,
        null=True,
        blank=True,
        related_name="fk",
        on_delete=models.CASCADE,
    )
    non_revisioned_many_to_many = models.ManyToManyField(
        NonRevisionedModel, blank=True, related_name="many"
    )

    class Revisions:
        related_strategy = "serialize"
