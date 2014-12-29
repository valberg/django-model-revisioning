# coding: utf-8

import difflib

from django.db import models


class RevisionQuerySet(models.QuerySet):
    def revisions(self):
        return self.filter(is_revision=True)

    def instances(self):
        return self.filter(is_revision=False)


class RevisionModel(models.Model):
    objects = RevisionQuerySet.as_manager()

    revision_at = models.DateTimeField(
        auto_now_add=True
    )

    is_revision = models.BooleanField(
        default=False,
    )

    revision_for = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='revision_set'
    )

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.old_data = self._get_instance_data()

    def _get_excluded_field_names(self):
        """
        Get the names of fields that should not be taken into consideration
        when checking if a revision should be made.

        :return: A list of strings
        """
        excluded_fields = ['id', 'is_revision', 'revision_for', 'revision_at']

        for field in self._meta.fields:
            # If there is a time-based field that has auto_now set to True,
            # then we don't want it in the comparison
            if isinstance(field, models.DateTimeField) \
                    or isinstance(field, models.DateField):

                if field.auto_now is True or field.auto_now_add is True:
                    excluded_fields.append(field.name)

        return excluded_fields

    def _get_instance_fields(self):
        """
        Get the actual fields that should not be taken into consideration
        when checking if a revision should be made.

        :return: A list of field instances
        """
        fields = []
        for field in self._meta.fields:
            if field.name in self._get_excluded_field_names():
                continue
            fields.append(field)

        return fields

    def _get_instance_data(self):
        """ Get the instance data.

        Used checking if a revision is required.

        :return: A dictionary that only contains data that is usable to
                 check if a revision is required.
        """
        data = dict()
        for field in self._get_instance_fields():
            # Get the value of the field and add it to the dict
            data[field.get_attname()] = field.value_from_object(self)

        return data

    def save(self, *args, **kwargs):
        has_changed = self.old_data != self._get_instance_data()

        if self.pk and has_changed and not self.is_revision:
            # Create a revision with old data:
            cls = self.__class__
            revision = cls(**self.old_data)
            revision.is_revision = True
            revision.revision_for = self
            revision.save()

            # Update the old data dict so that a revision does not get created
            # if an instance gets saved multiple times without changes
            self.__dict__['old_data'] = self._get_instance_data()

        super().save(*args, **kwargs)

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
        for field in self._get_instance_fields():
            field_diff = self._field_diff(other, field.name)
            if field_diff:
                output[field.name] = field_diff
        return output
