# coding: utf-8
from copy import deepcopy

from django.db import models
from django.db.models import Field
from django.db.models.base import ModelBase

from .options import RevisionOptions

excluded_field_names = ['revision_for', 'is_head', 'parent_revision']


class RevisionBase(ModelBase):

    revision_model_by_model = {}

    def __new__(mcs, name, bases, attrs):

        revision_attrs = deepcopy(attrs)

        revisions_options = attrs.pop('Revisions', None)

        new_class = super(RevisionBase, mcs).__new__(mcs, name, bases, attrs)
        new_class.add_to_class('_revisions', RevisionOptions(revisions_options))

        if new_class._meta.model_name != 'revisionmodel':
            revision_attrs = {key: val for key, val in revision_attrs.items()
                              if not isinstance(val, Field)}
            revision_attrs.update(
                {key: attrs[key] for key in new_class._revisions.fields})

            mcs._create_revisions_model(name, revision_attrs, new_class)

        if new_class._revisions.soft_deletion:
            new_class.add_to_class(
                'is_deleted', models.NullBooleanField(default=False))

        return new_class

    @classmethod
    def _create_revisions_model(mcs, name, attrs, revision_for,
                                handle_related=True, module=None):
        super_new = super(RevisionBase, mcs).__new__
        new_class_name = name + 'Revision'
        attrs['__qualname__'] = new_class_name

        from .models import Revision
        bases = (Revision,)

        related_fields = [
            field for field in revision_for._meta.fields
            if field.name not in excluded_field_names and
            (isinstance(field, models.ForeignKey) or
             isinstance(field, models.ManyToManyField))
        ]

        if handle_related and related_fields:
            attrs = mcs._handle_related_models(
                related_fields, attrs, revision_for)

        attrs['__module__'] = module if module else revision_for.__module__

        revision_class = super_new(mcs, new_class_name, bases, attrs)
        revision_class.add_to_class(
            'revision_for',
            models.ForeignKey(revision_for, related_name='revisions'),
        )
        revision_for.revision_class = revision_class

        return revision_class

    @classmethod
    def _handle_related_models(mcs, fields, attrs, cls):
        for field in fields:
            related_model = field.rel.to

            if related_model not in mcs.revision_model_by_model:

                new_attrs = {
                    field.name: field
                    for field in related_model._meta.fields
                    if isinstance(field, models.Field)
                    and field.name != 'id'
                }

                new_attrs['__module__'] = cls.__module__

                revision_class = mcs._create_revisions_model(
                    related_model.__name__,
                    new_attrs,
                    related_model,
                    handle_related=False,
                    module=cls.__module__
                )

                related_model.add_to_class('_revisions', RevisionOptions())

                related_model.revision_class = revision_class
                revision_class.revision_for_class = related_model

                old_save = deepcopy(related_model.save)

                from .models import RevisionModel
                related_model.current_revision = RevisionModel.current_revision
                related_model._get_instance_data =\
                    RevisionModel._get_instance_data

                def monkey_save(self, *args, **kwargs):
                    old_save(self, *args, **kwargs)
                    data = self._get_instance_data()
                    self.revision_class.objects.create(
                        revision_for=self, **data
                    )

                related_model.save = monkey_save
                mcs.revision_model_by_model[related_model] = revision_class
            else:
                revision_class = mcs.revision_model_by_model[related_model]

            new_field = None

            if isinstance(field, models.ForeignKey):
                new_field = models.ForeignKey(
                    revision_class,
                    related_name=field.related.get_accessor_name(),
                    verbose_name=field.verbose_name,
                    null=True,
                    blank=True,
                )
            elif isinstance(field, models.ManyToManyField):
                new_field = models.ManyToManyField(
                    revision_class,
                    related_name=field.related.get_accessor_name(),
                    verbose_name=field.verbose_name,
                    through=field.through,
                    null=True,
                    blank=True,
                )

            attrs[field.name] = new_field

        return attrs