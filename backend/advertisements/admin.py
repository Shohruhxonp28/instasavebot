from django.contrib import admin

from .models import Advertisement


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = (
        "title", "type", "placement", "active", "views", "clicks",
        "ctr_display", "start_date", "end_date",
    )
    list_filter = ("type", "placement", "active")
    search_fields = ("title", "content")
    readonly_fields = ("views", "clicks", "created_at", "updated_at")

    @admin.display(description="CTR")
    def ctr_display(self, obj):
        return f"{obj.ctr}%"
