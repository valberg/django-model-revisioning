# coding: utf-8
class RevisionOptions(object):
    """
    This class is basically a copy of the django.db.options.Options class
    """

    AVAILABLE_OPTIONS = ['fields', 'soft_deletion']

    def __init__(self, options=None):
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