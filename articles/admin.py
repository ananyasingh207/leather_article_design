from django.contrib import admin
from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'material', 'base_price', 'created_at')
    list_filter = ('category', 'material', 'created_at')
    search_fields = ('name', 'description', 'material')
    ordering = ('-created_at',)
    list_per_page = 20

