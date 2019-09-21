from copy import deepcopy

from django.db import models
from django.db.models import Field
from django.db.models.base import ModelBase

from .options import RevisionOptions

excluded_field_names = ["revision_for", "is_head", "parent_revision"]


class RevisionBase(ModelBase):

    revision_model_by_model = {}

    def __new__(mcs, name, bases, attrs, **kwargs):

        # import pdb; pdb.set_trace()

        if name == "RevisionModel":
            return super(RevisionBase, mcs).__new__(mcs, name, bases, attrs)

        revision_attrs = deepcopy(attrs)

        revisions_options = attrs.pop("Revisions", None)

        new_class = super(RevisionBase, mcs).__new__(mcs, name, bases, attrs)
        new_class.add_to_class("_revisions", RevisionOptions(revisions_options))

        if new_class._meta.model_name != "revisionmodel":
            revision_attrs = {
                key: val
                for key, val in revision_attrs.items()
                if not isinstance(val, Field)
            }
            revision_attrs.update(
                {key: attrs[key] for key in new_class._revisions.fields}
            )

            mcs._create_revisions_model(name, revision_attrs, new_class)

        if new_class._revisions.soft_deletion:
            new_class.add_to_class("is_deleted", models.NullBooleanField(default=False))

        return new_class

    @classmethod
    def _create_revisions_model(
        mcs, name, attrs, revision_for, handle_related=True, module=None
    ):
        super_new = super(RevisionBase, mcs).__new__
        new_class_name = name + "Revision"
        attrs["__qualname__"] = new_class_name

        from .models import Revision

        bases = (Revision,)

        related_fields = [
            deepcopy(field)
            for field in revision_for._meta.fields
            if field.name not in excluded_field_names
            and (
                isinstance(field, models.ForeignKey)
                or isinstance(field, models.ManyToManyField)
            )
            and not field.remote_field.model == revision_for
        ]

        self_referrers = [
            deepcopy(field)
            for field in revision_for._meta.fields
            if (
                isinstance(field, models.ForeignKey)
                or isinstance(field, models.ManyToManyField)
            )
            and field.remote_field.model == revision_for
        ]

        if handle_related and related_fields:
            attrs = mcs._handle_related_models(related_fields, attrs, revision_for)

        for field in self_referrers:
            del attrs[field.name]

        attrs["__module__"] = module if module else revision_for.__module__

        revision_class = super_new(mcs, new_class_name, bases, attrs)
        revision_class.add_to_class(
            "revision_for",
            models.ForeignKey(
                revision_for, related_name="revisions", on_delete=models.CASCADE
            ),
        )
        revision_for.revision_class = revision_class
        revision_class.revision_for_class = revision_for

        for field in self_referrers:
            field.model = revision_class
            field.remote_field.model = revision_class
            revision_class.add_to_class(field.name, field)

        mcs.revision_model_by_model[revision_for] = revision_class

        return revision_class

    @classmethod
    def _handle_related_models(mcs, fields, attrs, cls):
        from .models import RevisionModel

        for field in fields:
            related_model = field.remote_field.model

            if RevisionModel not in related_model.__bases__:
                continue

            if related_model not in mcs.revision_model_by_model:

                new_attrs = {
                    field.name: deepcopy(field)
                    for field in related_model._meta.fields
                    if isinstance(field, models.Field) and field.name != "id"
                }

                for attr in new_attrs.values():
                    if attr.unique:
                        attr._unique = False

                new_attrs["__module__"] = cls.__module__

                revision_class = mcs._create_revisions_model(
                    related_model.__name__,
                    new_attrs,
                    related_model,
                    handle_related=False,
                    module=cls.__module__,
                )

                related_model.add_to_class("_revisions", RevisionOptions())

                related_model.revision_class = revision_class
                revision_class.revision_for_class = related_model
                mcs.revision_model_by_model[related_model] = revision_class
            else:
                revision_class = mcs.revision_model_by_model[related_model]

            field.remote_field.model = revision_class
            attrs[field.name] = field

        return attrs
