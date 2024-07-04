from django.contrib import admin
from .models import AdminAdvertisement


@admin.register(AdminAdvertisement)
class AdminAdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_running', 'priority', 'created_at', 'updated_at')
    list_filter = ('is_running', 'priority')
    search_fields = ('title', 'details', 'discounts', 'offers', 'referral_code', 'guidelines', 'links')
    ordering = ('priority', 'created_at')
