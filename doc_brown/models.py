import difflib
from copy import deepcopy

from django.core import serializers
from django.db import models
from django.db.models import Field
from django.db.models.base import ModelBase
from django.utils import six


class Revision(models.Model):
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


def revision_on_delete(collector, field, sub_objs, using):
    serialized = serializers.serialize('json',
                                       [getattr(sub_objs[0], field.name)])
    for obj in sub_objs:
        setattr(obj, field.name, None)
        setattr(obj, field.name + '_serialized', serialized)
        obj.save()


def is_auto_now_field(field):
    if isinstance(field, models.DateField) or\
            isinstance(field, models.DateTimeField):
        return field.auto_now is True or field.auto_now_add is True


class RevisionOptions(object):
    """
    This class is basically a copy of the django.db.options.Options class
    """

    AVAILABLE_OPTIONS = ['fields', 'soft_deletion']

    def __init__(self, options):
        self.fields = '__all__'
        self.soft_deletion = False
        self.options = options

    def contribute_to_class(self, cls, name):
        cls._revisions = self

        field_names = [
            field.name for field in cls._meta.fields
            if field.name not in ['id', 'is_head']
        ]

        if self.options:
            options_attrs = self.options.__dict__.copy()

            for name in self.options.__dict__:
                if name.startswith('_'):
                    del options_attrs[name]

            for attr_name in self.AVAILABLE_OPTIONS:
                if attr_name in options_attrs:
                    if attr_name == 'fields' and\
                                    options_attrs['fields'] == '__all__':
                        setattr(self, attr_name, field_names)
                    else:
                        setattr(self, attr_name, options_attrs.pop(attr_name))
                else:
                    if attr_name == 'fields':
                        setattr(self, attr_name, field_names)
                    else:
                        setattr(
                            self, attr_name, getattr(self, attr_name))
        else:
            setattr(self, 'fields', field_names)


class RevisionBase(ModelBase):
    def __new__(mcs, name, bases, attrs):

        revision_attrs = deepcopy(attrs)
        revisions_options = attrs.pop('Revisions', None)

        new_class = super(RevisionBase, mcs).__new__(mcs, name, bases, attrs)
        new_class.add_to_class('_revisions', RevisionOptions(revisions_options))

        if new_class._meta.model_name != 'revisionmodel':
            revision_class = mcs._create_revisions_model(
                name, bases, revision_attrs, new_class)

            revision_class.add_to_class(
                'is_head', models.BooleanField(default=False))

            mcs._add_serialize_fields(revision_class)

        if new_class._revisions.soft_deletion:
            new_class.add_to_class(
                'is_deleted', models.BooleanField(default=False))

        mcs._add_serialize_fields(new_class)

        return new_class

    @classmethod
    def _add_serialize_fields(mcs, cls):
        for field in cls._meta.fields:
            exluded_field_names = ['revision_for', 'is_head']
            if isinstance(field, models.ForeignKey) and \
                    field.name not in exluded_field_names:

                field.null = True
                field.blank = True
                field.rel.on_delete = revision_on_delete
                new_field_name = field.name + '_serialized'
                cls.add_to_class(new_field_name,
                                 models.TextField(new_field_name,
                                                  null=True,
                                                  blank=True))

    @classmethod
    def _create_revisions_model(mcs, name, bases, attrs, cls):
        super_new = super(RevisionBase, mcs).__new__

        new_attrs = {key: val for key, val in attrs.items()
                     if not isinstance(val, Field)}

        revision_fields = {key: attrs[key] for key in cls._revisions.fields}

        new_attrs.update(revision_fields)
        new_class_name = name + 'Revision'
        new_attrs['__qualname__'] = new_class_name

        bases = (Revision,)
        revision_class = super_new(mcs, new_class_name, bases, new_attrs)
        revision_class.add_to_class(
            'revision_for',
            models.ForeignKey(cls, related_name='revisions'),
        )
        revision_class.add_to_class(
            'revision_at',
            models.DateTimeField(
                auto_now_add=True
            )
        )
        revision_class.add_to_class(
            'parent_revision',
            models.ForeignKey(
                'self', null=True, blank=True
            )
        )
        cls.revision_class = revision_class
        return revision_class


class RevisionModel(six.with_metaclass(RevisionBase, models.Model)):
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(RevisionModel, self).__init__(*args, **kwargs)
        self.old_data = self._get_instance_data()

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

    def _create_revision(self):
        self.revision_class.objects.create(
            revision_for=self,
            parent_revision=self.current_revision,
            **self.old_data
        )

    def save(self, *args, **kwargs):
        changing_head = kwargs.pop('changing_head', False)
        soft_deletion = kwargs.pop('soft_deletion', False)

        if not changing_head:
            if soft_deletion:
                self.is_deleted = True

            self.old_data = self._get_instance_data()

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

