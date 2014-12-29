from django.db import models


class RevisionQuerySet(models.QuerySet):
    def revisions(self):
        return self.filter(is_revision=True)

    def instances(self):
        return self.filter(is_revision=False)
