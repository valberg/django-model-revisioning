from django import template
from django.forms import model_to_dict

register = template.Library()


@register.simple_tag
def revision_as_dict(obj):
    excluded_fields = ["parent_revision", "is_head", "id", "original_object"]
    return model_to_dict(obj, exclude=excluded_fields)


@register.simple_tag
def get_attr(obj, attr):
    return getattr(obj, attr, "N/A")
