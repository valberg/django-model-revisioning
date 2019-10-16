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

        revision_attrs = {
            key: val
            for key, val in revision_attrs.items()
            if not isinstance(val, Field)
        }
        revision_attrs.update({key: attrs[key] for key in new_class._revisions.fields})

        mcs._create_revision_model(name, revision_attrs, new_class)

        if new_class._revisions.soft_deletion:
            new_class.add_to_class("is_deleted", models.NullBooleanField(default=False))

        return new_class

    @classmethod
    def _create_revision_model(mcs, name, attrs, original_model, module=None):
        new_class_name = name + "Revision"
        attrs["__qualname__"] = new_class_name

        from .models import Revision

        bases = (Revision,)

        attrs["__module__"] = module if module else original_model.__module__

        revision_class = super().__new__(mcs, new_class_name, bases, attrs)

        # for m2m_field in original_model.revisioned_m2m_fields:
        #     new_foreign_key_field = deepcopy(m2m_field)
        #
        #     if not isinstance(m2m_field.remote_field.through, RevisionModel):
        #         raise ImproperlyConfigured(
        #             "You should explicitly define a RevisionedManyToManyField's "
        #             "through model as a RevisionModel."
        #         )
        #
        #     if m2m_field.remote_field.model == original_model:
        #         # Self referral
        #         new_foreign_key_field.remote_field.model = revision_class
        #     else:
        #         new_foreign_key_field.remote_field.model = (
        #             m2m_field.remote_field.model.revision_class
        #         )
        #     revision_class.add_to_class(m2m_field.name, new_foreign_key_field)

        revision_class.add_to_class(
            "original_object",
            models.ForeignKey(
                original_model, related_name="revisions", on_delete=models.CASCADE
            ),
        )
        original_model.revision_class = revision_class

        revision_class.original_model_class = original_model

        return revision_class
