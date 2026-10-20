from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "published_at")
    search_fields = ("title",)
    ordering = ("-published_at",)


from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "post", "published_at")
    list_filter = ("published_at",)
    search_fields = ("text", "post__title", "author__username")
