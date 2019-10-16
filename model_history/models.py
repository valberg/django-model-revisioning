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

            # When creating a new revision we need to convert ForeignKeys
            if kwargs.get("force_insert", False):
                foreign_keys = [
                    field
                    for field in self._meta.get_fields()
                    if field.name not in excluded_field_names
                    and isinstance(field, RevisionedForeignKey)
                ]

                for field in foreign_keys:
                    pk = field.value_from_object(self)

                    if pk:
                        related_model_instance = field.related_model.original_model_class.objects.get(
                            pk=pk
                        )

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

        fields = filter(
            lambda f: f.name in self._revisions.fields
            or isinstance(f, RevisionedForeignKey),
            self._meta.fields,
        )

        for field in fields:
            # Get the value of the field and add it to the dict
            field_name = field.name
            if isinstance(field, models.ForeignKey):
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

        new_revision = self.revision_class(
            original_object=self, parent_revision=self.current_revision, **data
        )
        new_revision.save(force_insert=True)

        signals.post_revision.send(
            sender=self.__class__, instance=self, revision=new_revision
        )

    def save(
        self,
        *args,
        changing_head=False,
        soft_deletion=False,
        called_from_revision=False,
        **kwargs
    ):

        if not changing_head:
            if soft_deletion:
                self.is_deleted = True

        super().save(*args, **kwargs)

        if not changing_head:
            self.create_revision()

        # If this save is not called from a revision,
        # it means we have to do a "reverse save" on
        # all related RevisionModels
        if not called_from_revision:
            for obj in self._meta.related_objects:
                if issubclass(obj.related_model, RevisionModel):
                    kwargs = {obj.remote_field.name: self}
                    related_objects = obj.related_model.objects.filter(**kwargs)
                    for related_object in related_objects:
                        related_object.create_revision()

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

        foreign_key_fields = {
            field: field.value_from_object(revision)
            for field in self._meta.fields
            if isinstance(field, RevisionedForeignKey)
        }

        for fk_field, fk_value in foreign_key_fields.items():
            if fk_value:
                fk_object = getattr(self, fk_field.name)
                fk_object.set_head(str(fk_value))

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
