from django.contrib import admin

from doc_brown.admin import RevisionedModelAdmin

from . import models


class BarAdmin(RevisionedModelAdmin):
    model = models.Bar


class NonRevisionedModelAdmin(RevisionedModelAdmin):
    # This should show a message about the model not having revisions enabled.
    model = models.NonRevisionedModel


admin.site.register(models.Bar, BarAdmin)
admin.site.register(models.Baz)
admin.site.register(models.NonRevisionedModel, NonRevisionedModelAdmin)
admin.site.register(models.ModelWithoutOptions)
admin.site.register(models.SoftDeleted)

