from django.contrib import admin

from .models import Category, Location, Post, Comment

admin.site.empty_value_display = 'Не задано'


class PostInline(admin.StackedInline):
    model = Post
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at',
    )
    list_editable = (
        'is_published',
        'category',
    )
    search_fields = (
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
    )
    list_filter = (
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
    )
    list_display_links = ('title',)


admin.site.register(Location)
admin.site.register(Comment)
