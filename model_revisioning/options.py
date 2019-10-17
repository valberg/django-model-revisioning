from difflib import SequenceMatcher

from django.core.exceptions import ImproperlyConfigured

from model_revisioning.fields import RevisionedForeignKey


class RevisionOptions(object):
    """
    This class is basically a copy of the django.db.options.Options class
    """

    AVAILABLE_OPTIONS = ["fields", "soft_deletion"]

    def __init__(self, options=None):
        self.fields = "__all__"
        self.soft_deletion = False

        self.options = options

    def contribute_to_class(self, cls, name):
        cls._revisions = self

        field_names = [
            field.name
            for field in cls._meta.fields
            if field.name not in ["id", "is_head"]
            and not isinstance(field, RevisionedForeignKey)
        ]

        if self.options:
            options_attrs = self.options.__dict__.copy()

            for name in self.options.__dict__:
                # Get rid of __module__, __dict__, etc.
                if name.startswith("_"):
                    del options_attrs[name]
                    continue

                if name not in self.AVAILABLE_OPTIONS:
                    # If the given option is not one that is available
                    # we want to guide the user as best as possible.
                    # So we check if the name of the given option is
                    # similar to the ones available, and if so we suggest
                    # the closest match!
                    best_match = None
                    best_match_ratio = 0.7
                    for option in self.AVAILABLE_OPTIONS:
                        ratio = SequenceMatcher(a=name, b=option).ratio()
                        if ratio > best_match_ratio:
                            best_match = option
                            best_match_ratio = ratio

                    did_you_mean = ""
                    if best_match:
                        did_you_mean = f' Did you mean "{best_match}"?'

                    raise ImproperlyConfigured(
                        f'"{name}" is not a valid option for Revisions.{did_you_mean}'
                    )

            for attr_name in self.AVAILABLE_OPTIONS:
                if attr_name in options_attrs:
                    if attr_name == "fields" and options_attrs["fields"] == "__all__":
                        setattr(self, attr_name, field_names)
                    else:
                        setattr(self, attr_name, options_attrs.pop(attr_name))
                else:
                    if attr_name == "fields":
                        setattr(self, attr_name, field_names)
                    else:
                        setattr(self, attr_name, getattr(self, attr_name))
        else:
            setattr(self, "fields", field_names)
