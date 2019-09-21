from django.contrib import admin

from .models import Bar
from .models import Baz
from .models import ModelWithoutOptions
from .models import NonRevisionedModel
from .models import SoftDeleted
from model_history.admin import RevisionModelAdmin


@admin.register(Bar)
class BarAdmin(RevisionModelAdmin):
    list_display = ("char", "current_revision", "revisions_count")


@admin.register(Baz)
class BazAdmin(RevisionModelAdmin):
    list_display = ("char", "current_revision", "revisions_count")


admin.site.register(ModelWithoutOptions)
admin.site.register(SoftDeleted)
admin.site.register(NonRevisionedModel)
