import difflib

from django.db import models
from django.utils import six
from django_extensions.db.fields import ShortUUIDField

from .base import RevisionBase
from .managers import RevisionedModelManager


class Revision(models.Model):

    id = ShortUUIDField(primary_key=True)

    class Meta:
        abstract = True

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

        self.revision_class.objects.create(
            revision_for=self,
            parent_revision=self.current_revision,
            **data
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
        if type(revision) == str:
            revision = self.revisions.get(pk=revision)

        fields = {field: self._meta.get_field(field).value_from_object(revision)
                  for field in self._revisions.fields}

        for name, value in fields.items():
            setattr(self, name, value)

        self.save(changing_head=True)

        revision.save()

    def _field_diff(self, other, field):

        # Get the field content from the respective instances.
        # Check if they are None, if so then make them be an empty string
        a = getattr(self, field) if getattr(self, field) else ''
        b = getattr(other, field) if getattr(other, field) else ''

        if type(a) != str or type(b) != str:
            return None

        if type(a) != list:
            a = a.split('\n')

        if type(b) != list:
            b = b.split('\n')

        if a == b:
            return None

        return difflib.ndiff(b, a)

    def diff_field(self, other, field):
        return self._field_diff(other, field)

    def diff_all(self, other):
        output = dict()
        for field in self._get_fields():
            field_diff = self._field_diff(other, field.name)
            if field_diff:
                output[field.name] = field_diff
        return output

