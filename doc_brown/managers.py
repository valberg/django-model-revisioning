from django.db import models


class RevisionedModelQuerySet(models.QuerySet):
    def update(self, **kwargs):

        for instance in self.all():
            instance._create_revision(**kwargs)

        super(RevisionedModelQuerySet, self).update(**kwargs)


class RevisionedModelManager(models.Manager):
    def get_queryset(self):
        return RevisionedModelQuerySet(self.model, using=self._db)
