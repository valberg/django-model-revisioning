# coding: utf-8
from django.db import models


class ModelHistoryQuerySet(models.QuerySet):
    def update(self, **kwargs):

        for instance in self.all():
            instance.create_revision(**kwargs)

        super(ModelHistoryQuerySet, self).update(**kwargs)


class ModelHistoryManager(models.Manager):
    def get_queryset(self):
        return ModelHistoryQuerySet(self.model, using=self._db)
