from copy import deepcopy

from django.db import models
from django.db.models import Field
from django.db.models.base import ModelBase

from .utils import revision_on_delete
from .options import RevisionOptions


class RevisionBase(ModelBase):
    def __new__(mcs, name, bases, attrs):

        revision_attrs = deepcopy(attrs)
        revisions_options = attrs.pop('Revisions', None)

        new_class = super(RevisionBase, mcs).__new__(mcs, name, bases, attrs)
        new_class.add_to_class('_revisions', RevisionOptions(revisions_options))

        if new_class._meta.model_name != 'revisionmodel':
            revision_class = mcs._create_revisions_model(
                name, bases, revision_attrs, new_class)

            revision_class.add_to_class(
                'is_head', models.BooleanField(default=False))

            mcs._add_serialize_fields(revision_class)

        if new_class._revisions.soft_deletion:
            new_class.add_to_class(
                'is_deleted', models.BooleanField(default=False))

        mcs._add_serialize_fields(new_class)

        return new_class

    @classmethod
    def _add_serialize_fields(mcs, cls):
        for field in cls._meta.fields:
            exluded_field_names = ['revision_for', 'is_head']
            if isinstance(field, models.ForeignKey) and \
                    field.name not in exluded_field_names:

                field.null = True
                field.blank = True
                field.rel.on_delete = revision_on_delete
                new_field_name = field.name + '_serialized'
                cls.add_to_class(new_field_name,
                                 models.TextField(new_field_name,
                                                  null=True,
                                                  blank=True))

    @classmethod
    def _create_revisions_model(mcs, name, bases, attrs, cls):
        super_new = super(RevisionBase, mcs).__new__

        new_attrs = {key: val for key, val in attrs.items()
                     if not isinstance(val, Field)}

        revision_fields = {key: attrs[key] for key in cls._revisions.fields}

        new_attrs.update(revision_fields)
        new_class_name = name + 'Revision'
        new_attrs['__qualname__'] = new_class_name

        from .models import Revision
        bases = (Revision,)
        revision_class = super_new(mcs, new_class_name, bases, new_attrs)
        revision_class.add_to_class(
            'revision_for',
            models.ForeignKey(cls, related_name='revisions'),
        )
        cls.revision_class = revision_class
        return revision_class