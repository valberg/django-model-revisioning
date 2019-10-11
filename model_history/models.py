import uuid

from django.db import models

from . import signals
from .base import excluded_field_names
from .base import RevisionBase
from .fields import RevisionedForeignKey
from .managers import ModelHistoryManager


class Revision(models.Model):
    """ Model for revisions. """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    revision_at = models.DateTimeField(auto_now_add=True)

    parent_revision = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children_revisions",
        on_delete=models.CASCADE,
    )

    is_head = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = ["revision_at"]

    def save(self, *args, **kwargs):
        if kwargs.pop("remove_head", None):
            self.is_head = False
        else:
            self.make_head()

            related_fields = [
                field
                for field in self._meta.get_fields()
                if field.name not in excluded_field_names
                and (field.is_relation and not field.auto_created)
                and (Revision in field.remote_field.model.__bases__)
            ]

            for field in related_fields:
                pk = field.value_from_object(self)
                if pk:
                    related_model_instance = field.related_model.original_model_class.objects.get(
                        pk=pk
                    )

                    if not isinstance(
                        self.original_object, field.related_model.original_model_class
                    ):
                        related_model_instance.save()

                    if self.original_object == related_model_instance:
                        # The object is referring to itself
                        self.__dict__[field.name + "_id"] = self.id
                    else:
                        self.__dict__[
                            field.name + "_id"
                        ] = related_model_instance.current_revision.id

        super().save(*args, **kwargs)

    def make_head(self):
        """ Make this revision to head. """
        current_head = self.original_object.current_revision
        if current_head:
            current_head.save(remove_head=True)
        self.is_head = True

    def __str__(self):
        return str(self.id)


class RevisionModel(models.Model, metaclass=RevisionBase):
    """ Model to inherit from to enable revisioning. """

    objects = ModelHistoryManager()

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
            if field.name in self._revisions.fields or isinstance(
                field, RevisionedForeignKey
            ):
                # Get the value of the field and add it to the dict
                field_name = field.name
                if isinstance(field, RevisionedForeignKey):
                    field_name += "_id"
                data[field_name] = field.value_from_object(self)
        return data

    def create_revision(self, **kwargs):
        """ Create revision for this instance.

        :param kwargs: A dict of data to be used as the data for the revision.
                       (Optional)
        :return revision: The created revision.
        """

        data = self._get_instance_data()
        if kwargs:
            data = kwargs

        signals.pre_revision.send(sender=self.__class__, instance=self)

        new_revision = self.revisions.create(
            original_object=self, parent_revision=self.current_revision, **data
        )

        signals.post_revision.send(
            sender=self.__class__, instance=self, revision=new_revision
        )

    def save(self, *args, **kwargs):
        changing_head = kwargs.pop("changing_head", False)
        soft_deletion = kwargs.pop("soft_deletion", False)

        if not changing_head:
            if soft_deletion:
                self.is_deleted = True

        super().save(*args, **kwargs)

        # If referring_to_self is set the we already have a revision
        if not changing_head:
            self.create_revision()

    def delete(self, using=None):
        if self._revisions.soft_deletion:
            self.save(using=using, soft_deletion=True)
        else:
            super().delete(using=using)

    @property
    def current_revision(self):
        try:
            return self.revisions.get(is_head=True)
        except self.revision_class.DoesNotExist:
            return None

    def set_head(self, revision):
        """ Set the head of this instance to the given revision.

        :param revision: The revision to set as head.
        """

        old_head = self.current_revision

        signals.pre_change_head.send(
            sender=self.__class__,
            instance=self,
            current_head=self.current_revision,
            future_head=revision,
        )

        if type(revision) == str:
            revision = self.revisions.get(pk=revision)

        if revision.original_object != self:
            raise Exception(
                "The given revision ({}) is not a revision of "
                "this instance ({})".format(revision, self)
            )

        fields = {
            field: self._meta.get_field(field).value_from_object(revision)
            for field in self._revisions.fields
        }

        for name, value in fields.items():
            setattr(self, name, value)

        self.save(changing_head=True)

        revision.save()

        signals.post_change_head.send(
            sender=self.__class__, instance=self, old_head=old_head, new_head=revision
        )

    def revisions_count(self):
        """ Get the number of revisions for this instance.
        :return: Number of revisions.
        """
        return self.revisions.count()
