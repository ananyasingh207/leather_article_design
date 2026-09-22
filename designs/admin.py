from django.contrib import admin
from .models import Design


@admin.register(Design)
class DesignAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'user',
        'article',
        'leather_type',
        'leather_color',
        'leather_finish',
        'stitching_color',
        'created_at',
    )
    list_filter = (
        'leather_type',
        'leather_color',
        'leather_finish',
        'stitching_color',
        'font',
        'created_at',
    )
    search_fields = (
        'name',
        'user__username',
        'user__email',
        'article__name',
        'custom_text',
    )
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
