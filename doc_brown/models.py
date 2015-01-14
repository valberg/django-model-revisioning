import difflib
from copy import deepcopy

from django.core import serializers
from django.db import models
from django.db.models import Field
from django.db.models.base import ModelBase
from django.utils import six


def revision_on_delete(collector, field, sub_objs, using):
    serialized = serializers.serialize('json',
                                       [getattr(sub_objs[0], field.name)])

    for obj in sub_objs:
        setattr(obj, field.name, None)
        setattr(obj, field.name + '_serialized', serialized)
        obj.save()


def auto_now_field(field):
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
        if self.options:
            options_attrs = self.options.__dict__.copy()
            for name in self.options.__dict__:
                if name.startswith('_'):
                    del options_attrs[name]
            for attr_name in self.AVAILABLE_OPTIONS:
                if attr_name in options_attrs:
                    if attr_name == 'fields' and\
                                    options_attrs['fields'] == '__all__':
                        setattr(self, attr_name,
                                [field.name for field in cls._meta.fields
                                 if field.name != 'id'])
                    else:
                        setattr(self, attr_name, options_attrs.pop(attr_name))
                elif hasattr(self.options, attr_name):
                    setattr(self, attr_name, getattr(self.options, attr_name))


class RevisionBase(ModelBase):
    def __new__(mcs, name, bases, attrs):

        revision_attrs = deepcopy(attrs)
        revisions_options = attrs.pop('Revisions', None)

        new_class = super(RevisionBase, mcs).__new__(mcs, name, bases, attrs)
        new_class.add_to_class('_revisions', RevisionOptions(revisions_options))

        revision_class = mcs._create_revisions_model(
            name, bases, revision_attrs, new_class)

        if new_class._revisions.soft_deletion:
            new_class.add_to_class(
                'is_deleted', models.BooleanField(default=False))

        mcs._add_serialize_fields(new_class)
        mcs._add_serialize_fields(revision_class)

        return new_class

    @classmethod
    def _add_serialize_fields(mcs, cls):
        for field in cls._meta.fields:
            exluded_field_names = ['revision_for']
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

        revision_fields = cls._revisions.fields
        if type(revision_fields) == str and revision_fields == '__all__':
            revision_fields = {
                key: val for key, val in attrs.items()
                if isinstance(val, Field) and not auto_now_field(val)
            }
        elif type(revision_fields) == list:
            revision_fields = {key: attrs[key] for key in revision_fields}

        new_attrs.update(revision_fields)
        new_class_name = name + 'Revision'
        new_attrs['__qualname__'] = new_class_name

        revision_class = super_new(mcs, new_class_name, bases, new_attrs)
        revision_class.add_to_class(
            'revision_for',
            models.ForeignKey(cls)
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
        super().__init__(*args, **kwargs)
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

    def save(self, *args, **kwargs):
        new_data = self._get_instance_data()
        has_changed = self.old_data != new_data

        if kwargs.pop('soft_deletion', None):
            self.is_deleted = True

        if self.pk and has_changed:
            parent_revision = self.revision_class.objects.last()
            self.revision_class.objects.create(
                revision_for=self,
                parent_revision=parent_revision,
                **self.old_data
            )

        # Update the old data dict so that a revision does not get created
        # if an instance gets saved multiple times without changes
        self.old_data = self._get_instance_data()
        super().save(*args, **kwargs)

    def delete(self, using=None):
        if self._revisions.soft_deletion:
            self.save(using=using, soft_deletion=True)
        else:
            super(RevisionModel, self).delete(using=using)

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

