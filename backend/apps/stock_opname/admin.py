from django.contrib import admin
from .models import StockOpname, StockOpnameItem


class StockOpnameItemInline(admin.TabularInline):
    model = StockOpnameItem
    extra = 0
    readonly_fields = ('stock', 'system_quantity', 'actual_quantity', 'notes')


@admin.register(StockOpname)
class StockOpnameAdmin(admin.ModelAdmin):
    list_display = (
        'document_number', 'period_type', 'period_start', 'period_end',
        'status', 'created_by', 'created_at',
    )
    list_filter = ('status', 'period_type')
    search_fields = ('document_number',)
    inlines = [StockOpnameItemInline]
    date_hierarchy = 'created_at'
    list_per_page = 25
