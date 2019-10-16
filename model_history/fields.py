from copy import deepcopy
from functools import partial

from django.db import models
from django.db.models.utils import make_model_tuple


class RevisionedForeignKey(models.ForeignKey):
    def contribute_to_class(self, cls, name, private_only=False, **kwargs):
        from model_history.models import Revision

        super().contribute_to_class(cls, name, private_only=private_only, **kwargs)

        if issubclass(cls, Revision) or cls.__module__ == "__fake__":
            return

        def add_field_to_revision(
            model, related_model, revision_model, related_revision_model, field
        ):
            new_field = deepcopy(field)

            if model == related_model:
                new_field.remote_field.model = revision_model
            else:
                new_field.remote_field.model = related_revision_model

            new_field.remote_field.related_name = "+"
            revision_model.add_to_class(field.name, new_field)

        remote_model = self.remote_field.model
        if remote_model == "self":
            remote_model = cls

        if isinstance(remote_model, str):
            remote_model_name = remote_model
        else:
            remote_model_name = (
                remote_model._meta.app_label + "." + remote_model.__name__
            )

        ms = [
            cls,
            remote_model,
            cls._meta.app_label + "." + cls.__name__ + "Revision",
            remote_model_name + "Revision",
        ]

        model_keys = (make_model_tuple(m) for m in ms)
        cls._meta.apps.lazy_model_operation(
            partial(add_field_to_revision, field=self), *model_keys
        )


class RevisionedManyToManyField(models.ManyToManyField):
    def contribute_to_class(self, cls, name, private_only=False, **kwargs):
        # TODO: Implement this!

        super().contribute_to_class(cls, name, private_only=private_only, **kwargs)
