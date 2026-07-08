from django.contrib import admin
from unfold import admin as unfold_admin

from .models import Service, ServiceInclude


class ServiceIncludeInline(unfold_admin.TabularInline):
    model = ServiceInclude
    extra = 1


@admin.register(Service)
class ServiceAdmin(unfold_admin.ModelAdmin):
    inlines = [ServiceIncludeInline]
