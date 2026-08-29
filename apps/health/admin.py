from django.contrib import admin
from .models import WellnessTip, Medicine, MedicineLog, HydrationLog

@admin.register(WellnessTip)
class WellnessTipAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'action_label', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'tip_text')

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'dosage', 'frequency', 'start_date', 'end_date', 'is_active')
    list_filter = ('frequency', 'is_active')
    search_fields = ('name', 'user__username')

@admin.register(MedicineLog)
class MedicineLogAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'user', 'scheduled_date', 'scheduled_time', 'status', 'logged_at')
    list_filter = ('status', 'scheduled_date')

@admin.register(HydrationLog)
class HydrationLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'glasses', 'logged_at')
