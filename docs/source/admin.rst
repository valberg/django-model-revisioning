Admin integration
=================

Getting a interface for viewing revision, and even changing the current head,
is quite easy. Simply use ``RevisionedModelAdmin`` as such::

    from django.contrib import admin
    from model_history.admin import RevisionedModelAdmin
    from .models import Bar

    admin.site.register(Bar, RevisionedModelAdmin)


Since ``RevisionedModelAdmin`` inherits from ``ModelAdmin``, it is possible to
extend the admin as usual::

    from django.contrib import admin
    from model_history.admin import RevisionModelAdmin
    from .models import Bar

    class BarAdmin(RevisionModelAdmin):
        list_display = ('char', 'current_revision', 'revisions_count')

    admin.site.register(Bar, BarAdmin)
