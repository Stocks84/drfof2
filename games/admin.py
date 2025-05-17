from django.contrib import admin
from .models import Game, Like, Comment

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'creator__username')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'created_at')
    search_fields = ('user__username', 'game__title')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'text', 'created_at')
    search_fields = ('user__username', 'game__title', 'text')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
