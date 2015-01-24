from django.db import models
from django.utils import six
from django_extensions.db.fields import ShortUUIDField

from . import signals
from .base import RevisionBase
from .managers import RevisionedModelManager


class Revision(models.Model):

    id = ShortUUIDField(primary_key=True)
    revision_at = models.DateTimeField(auto_now_add=True)
    parent_revision = models.ForeignKey('self', null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ['revision_at']

    def save(self, *args, **kwargs):
        self.is_head = True
        if kwargs.pop('remove_head', None):
            self.is_head = False
        else:
            self.update_head()
        super(Revision, self).save(*args, **kwargs)

    @classmethod
    def update_head(cls):
        try:
            current_head = cls.objects.get(is_head=True)
            current_head.save(remove_head=True)
        except cls.DoesNotExist:
            pass

    def __str__(self):
        return str(self.id)


class RevisionModel(six.with_metaclass(RevisionBase, models.Model)):

    objects = RevisionedModelManager()

    class Meta:
        abstract = True

    def _get_instance_data(self):
        """ Get the instance data.

        Used checking if a revision is required.

        :return: A dictionary that only contains data that is usable to
                 check if a revision is required.
        """
        data = dict()
        for field in self._meta.fields:
            if field.name in self._revisions.fields:
                # Get the value of the field and add it to the dict
                field_name = field.name
                if isinstance(field, models.ForeignKey):
                    field_name += '_id'
                data[field_name] = field.value_from_object(self)
        return data

    def _create_revision(self, **kwargs):
        data = self._get_instance_data()
        if kwargs:
            data = kwargs

        signals.pre_revision.send(
            sender=self.__class__,
            instance=self,
        )

        new_revision = self.revisions.create(
            revision_for=self,
            parent_revision=self.current_revision,
            **data
        )

        signals.post_revision.send(
            sender=self.__class__,
            instance=self,
            revision=new_revision
        )

    def save(self, *args, **kwargs):
        changing_head = kwargs.pop('changing_head', False)
        soft_deletion = kwargs.pop('soft_deletion', False)

        if not changing_head:
            if soft_deletion:
                self.is_deleted = True

        super(RevisionModel, self).save(*args, **kwargs)

        if not changing_head:
            self._create_revision()

    def delete(self, using=None):
        if self._revisions.soft_deletion:
            self.save(using=using, soft_deletion=True)
        else:
            super(RevisionModel, self).delete(using=using)

    @property
    def current_revision(self):
        try:
            return self.revisions.get(is_head=True)
        except self.revision_class.DoesNotExist:
            return None

    def set_head_to(self, revision):

        signals.pre_change_head.send(
            sender=self.__class__,
            instance=self,
            current_head=self.current_revision,
        )

        if type(revision) == str:
            revision = self.revisions.get(pk=revision)

        fields = {field: self._meta.get_field(field).value_from_object(revision)
                  for field in self._revisions.fields}

        for name, value in fields.items():
            setattr(self, name, value)

        self.save(changing_head=True)

        revision.save()

        signals.post_change_head.send(
            sender=self.__class__,
            instance=self,
            current_head=revision,
        )
