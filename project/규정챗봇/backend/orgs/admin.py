from django.contrib import admin
from unfold.admin import ModelAdmin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from orgs.models import OrganizationUnit, StaffProfile


@admin.register(OrganizationUnit)
class OrganizationUnitAdmin(ModelAdmin, TreeAdmin):
    form = movenodeform_factory(OrganizationUnit)
    list_display = ("name", "kind", "is_active", "updated_at")
    list_filter = ("kind", "is_active")
    search_fields = ("name",)


@admin.register(StaffProfile)
class StaffProfileAdmin(ModelAdmin):
    list_display = (
        "display_name",
        "organization",
        "position",
        "extension",
        "email",
        "is_active",
    )
    list_filter = ("organization", "position", "is_active", "is_demo")
    search_fields = ("display_name", "email", "duty_keywords")

# Register your models here.
