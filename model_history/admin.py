# coding: utf-8
from django.contrib.admin import ModelAdmin
from django.contrib.admin.utils import unquote
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _

from .models import RevisionModel


class RevisionModelAdmin(ModelAdmin):
    change_form_template = "doc_brown/change_form.html"

    def __init__(self, model, admin_site):
        if RevisionModel not in model.__bases__:
            raise ImproperlyConfigured("Model {} is not versioned.".format(model))
        super().__init__(model, admin_site)

    def get_urls(self):
        from django.conf.urls import url

        urlpatterns = super(RevisionModelAdmin, self).get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name

        urlpatterns = [
            url(
                r"^(.+)/revisions/$",
                self.admin_site.admin_view(self.revisions_view),
                name="%s_%s_revisions" % info,
            )
        ] + urlpatterns

        return urlpatterns

    def revisions_view(self, request, object_id, extra_context=None):

        model = self.model
        obj = get_object_or_404(self.get_queryset(request), pk=unquote(object_id))

        if request.POST:
            revision_id = request.POST.get("revision_id", None)
            obj.set_head(revision_id)

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        opts = model._meta

        try:
            revisions = obj.revisions.all()
        except AttributeError:
            revisions = None

        context = dict(
            self.admin_site.each_context(request),
            title=_("Revisions: %s") % force_text(obj),
            module_name=capfirst(force_text(opts.verbose_name_plural)),
            object=obj,
            opts=opts,
            media=self.media,
            preserved_filters=self.get_preserved_filters(request),
            revisions=revisions,
        )

        context.update(extra_context or {})
        return TemplateResponse(request, "doc_brown/revisions.html", context)
