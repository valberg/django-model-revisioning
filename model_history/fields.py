from django.db import models


class RevisionedForeignKey(models.ForeignKey):
    def contribute_to_class(self, cls, name, private_only=False, **kwargs):
        from model_history.models import RevisionModel

        if issubclass(cls, RevisionModel):
            cls.revisioned_foreign_keys.append(self)
        super().contribute_to_class(cls, name, private_only=private_only, **kwargs)
