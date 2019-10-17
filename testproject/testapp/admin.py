from django.contrib import admin

from .models import Bar
from .models import Baz
from .models import ModelOnOtherEndOfRevisionedForeignKey
from .models import ModelWithoutOptions
from .models import ModelWithRevisionedForeignKey
from .models import NonRevisionedModel
from .models import SoftDeleted
from model_revisioning.admin import RevisionModelAdmin


@admin.register(Bar)
class BarAdmin(RevisionModelAdmin):
    list_display = ("char", "current_revision", "revisions_count")


@admin.register(Baz)
class BazAdmin(RevisionModelAdmin):
    list_display = ("char", "current_revision", "revisions_count")


@admin.register(ModelOnOtherEndOfRevisionedForeignKey)
class ModelOnOtherEndOfRevisionedForeignKeyAdmin(RevisionModelAdmin):
    list_display = ("char", "current_revision", "revisions_count")


@admin.register(ModelWithRevisionedForeignKey)
class ModelWithRevisionedForeignKey(RevisionModelAdmin):
    list_display = ("current_revision", "revisions_count")


admin.site.register(ModelWithoutOptions)
admin.site.register(SoftDeleted)
admin.site.register(NonRevisionedModel)
