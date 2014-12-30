from copy import deepcopy
from django.db import models
from django.db.models.base import ModelBase
from django.utils import six


class RevisionMeta(ModelBase):
    def __new__(cls, name, bases, attrs):
        super_new = super(RevisionMeta, cls).__new__

        revision_attrs = deepcopy(attrs)

        actual_class = super_new(cls, name, bases, attrs)

        revision_class = super_new(cls, name + 'Revisions', bases,
                                   revision_attrs)
        revision_class.add_to_class(
            'revision_for',
            models.ForeignKey(actual_class)
        )

        return actual_class


class RevisionTwoTablesModel(six.with_metaclass(RevisionMeta, models.Model)):
    class Meta:
        abstract = True