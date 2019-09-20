from django.contrib import admin

from . import models
from model_history.admin import RevisionModelAdmin


class BarAdmin(RevisionModelAdmin):
    list_display = ("char", "current_revision", "revisions_count")


admin.site.register(models.Bar, BarAdmin)
admin.site.register(models.Baz)
admin.site.register(models.ModelWithoutOptions)
admin.site.register(models.SoftDeleted)

# The following should show a message about the model not being revisioned
admin.site.register(models.NonRevisionedModel, RevisionModelAdmin)
