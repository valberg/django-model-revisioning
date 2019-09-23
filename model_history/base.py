from copy import deepcopy

from django.db import models
from django.db.models import Field
from django.db.models.base import ModelBase

from .options import RevisionOptions

excluded_field_names = ["original_object", "is_head", "parent_revision"]


class RevisionBase(ModelBase):

    revision_model_by_model = {}

    def __new__(mcs, name, bases, attrs, **kwargs):

        if name == "RevisionModel":
            return super(RevisionBase, mcs).__new__(mcs, name, bases, attrs)

        revision_attrs = deepcopy(attrs)

        revisions_options = attrs.pop("Revisions", None)

        new_class = super().__new__(mcs, name, bases, attrs)
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
        mcs, name, attrs, original_model, handle_related=True, module=None
    ):
        new_class_name = name + "Revision"
        attrs["__qualname__"] = new_class_name

        from .models import Revision

        bases = (Revision,)

        related_fields = [
            deepcopy(field)
            for field in original_model._meta.fields
            if field.name not in excluded_field_names
            and (
                isinstance(field, models.ForeignKey)
                or isinstance(field, models.ManyToManyField)
            )
            and not field.remote_field.model == original_model
        ]

        self_referrers = [
            deepcopy(field)
            for field in original_model._meta.fields
            if (
                isinstance(field, (models.ForeignKey, models.ManyToManyField))
                and field.remote_field.model == original_model
            )
        ]

        if handle_related and related_fields:
            attrs = mcs._handle_related_models(related_fields, attrs, original_model)

        for field in self_referrers:
            del attrs[field.name]

        attrs["__module__"] = module if module else original_model.__module__

        revision_class = super().__new__(mcs, new_class_name, bases, attrs)
        revision_class.add_to_class(
            "original_object",
            models.ForeignKey(
                original_model, related_name="revisions", on_delete=models.CASCADE
            ),
        )
        original_model.revision_class = revision_class
        revision_class.original_model_class = original_model

        for field in self_referrers:
            field.model = revision_class
            field.remote_field.model = revision_class
            revision_class.add_to_class(field.name, field)

        mcs.revision_model_by_model[original_model] = revision_class

        return revision_class

    @classmethod
    def _handle_related_models(mcs, fields, attrs, cls):

        # TODO: Is this needed? If the related field points to a revisioned model,
        #  we should point to that revisioned model, otherwise it should be the same as the original model

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
                revision_class.original_model_class = related_model
                mcs.revision_model_by_model[related_model] = revision_class
            else:
                revision_class = mcs.revision_model_by_model[related_model]

            field.remote_field.model = revision_class
            attrs[field.name] = field

        return attrs
