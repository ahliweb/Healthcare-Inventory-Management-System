from django.contrib import admin
from .models import Recall, RecallItem


class RecallItemInline(admin.TabularInline):
    model = RecallItem
    extra = 1
    autocomplete_fields = ['item', 'stock']


@admin.register(Recall)
class RecallAdmin(admin.ModelAdmin):
    list_display = ('document_number', 'recall_date', 'supplier', 'status', 'created_by')
    list_filter = ('status', 'recall_date', 'supplier')
    search_fields = ('document_number', 'supplier__name')
    readonly_fields = ('created_at', 'updated_at', 'verified_at')
    inlines = [RecallItemInline]
    autocomplete_fields = ['supplier', 'created_by', 'verified_by']

    fieldsets = (
        ('Informasi Recall', {
            'fields': (
                'document_number',
                'recall_date',
                'supplier',
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
