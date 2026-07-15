from django.contrib import admin

from .models import BotUser


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = (
        "telegram_id", "username", "language", "is_premium",
        "is_blocked", "download_count_display", "last_activity_at", "created_at",
    )
    list_filter = ("language", "is_premium", "is_blocked", "is_active")
    search_fields = ("telegram_id", "username", "first_name")
    readonly_fields = ("created_at", "updated_at", "last_activity_at")
    actions = ["block_users", "unblock_users"]

    @admin.display(description="Downloads")
    def download_count_display(self, obj):
        return obj.download_count

    @admin.action(description="Block selected users")
    def block_users(self, request, queryset):
        queryset.update(is_blocked=True)

    @admin.action(description="Unblock selected users")
    def unblock_users(self, request, queryset):
        queryset.update(is_blocked=False)
