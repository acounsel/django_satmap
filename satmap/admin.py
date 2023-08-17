from django.contrib import admin
from .models import Layer, Map, Project
from django.urls import reverse
from django.http import HttpResponseRedirect

from .models import Layer

class LayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'band', 'min', 'max')
    actions = ['duplicate_selected']

    def duplicate_selected(self, request, queryset):
        for obj in queryset:
            obj.id = None
            obj.name = f"{obj.name} (Copy)"
            obj.save()

        model_name = self.model._meta.verbose_name_plural.replace(' ', '_')
        return HttpResponseRedirect(reverse(f'admin:{model_name}_changelist'))
    duplicate_selected.short_description = "Duplicate selected %(verbose_name_plural)s"

admin.site.register(Layer, LayerAdmin)
admin.site.register(Map)
admin.site.register(Project)