from django.db import models
from doc_brown import RevisionModel


class NonRevisionedModel(models.Model):
    char = models.CharField(max_length=255, null=True, blank=True)


class Bar(RevisionModel):
    char = models.CharField(max_length=255, null=True, blank=True)
    int = models.IntegerField(null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    boolean = models.BooleanField(default=False)
    null_boolean = models.NullBooleanField()

    hello_world = models.CharField(max_length=255, null=True, blank=True)

    non_revisioned_foreign_key = models.ForeignKey(
        'testapp.NonRevisionedModel',
        null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True, auto_now=True)

    class Revisions:
        fields = '__all__'


class Baz(RevisionModel):
    char = models.CharField(max_length=255, null=True, blank=True)
    int = models.IntegerField(null=True, blank=True)
    text = models.TextField(null=True, blank=True)

    class Revisions:
        fields = ['char', 'text']


class SoftDeleted(RevisionModel):
    content = models.TextField()

    class Revisions:
        soft_deletion = True


class ModelWithoutOptions(RevisionModel):
    content = models.TextField()
