from django.core import serializers
from django.db import models


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