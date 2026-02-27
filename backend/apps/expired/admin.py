from django.contrib import admin
from .models import Expired, ExpiredItem


class ExpiredItemInline(admin.TabularInline):
    model = ExpiredItem
    extra = 1
    autocomplete_fields = ['item', 'stock']


@admin.register(Expired)
class ExpiredAdmin(admin.ModelAdmin):
    list_display = ('document_number', 'report_date', 'status', 'created_by')
    list_filter = ('status', 'report_date')
    search_fields = ('document_number',)
    readonly_fields = ('created_at', 'updated_at', 'verified_at')
    inlines = [ExpiredItemInline]
    autocomplete_fields = ['created_by', 'verified_by']

    fieldsets = (
        ('Informasi Expired', {
            'fields': (
                'document_number',
                'report_date',
                'status'
            )
        }),
        ('Otorisasi & Catatan', {
            'fields': (
                'notes',
                'created_by',
                'verified_by',
                'verified_at',
            )
        }),
        ('Audit Trail', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
    )
