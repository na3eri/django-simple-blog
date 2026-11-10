from django.contrib import admin

from .models import Article, Category, Comment, Message


# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "user_profile", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "user_profile",
        "status",
        "views",
        "created_at",
    )
    list_filter = ("status", "category", "is_comment_enabled", "is_deleted")
    search_fields = ("title", "excerpt", "content")
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Comment)
admin.site.register(Message)
