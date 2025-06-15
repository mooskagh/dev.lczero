from django.contrib import admin

from .models import Artifact, Revision, Target


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']
    search_fields = ['id', 'name']


@admin.register(Revision)
class RevisionAdmin(admin.ModelAdmin):
    list_display = [
        'commit_hash',
        'datetime',
        'pr_number',
        'tag_description',
        'is_pinned',
        'is_scheduled_for_deletion',
        'is_hidden',
    ]
    list_filter = ['is_pinned', 'is_scheduled_for_deletion', 'is_hidden', 'datetime']
    search_fields = ['commit_hash', 'tag_description']
    readonly_fields = ['created_at']


@admin.register(Artifact)
class ArtifactAdmin(admin.ModelAdmin):
    list_display = ['filename', 'revision', 'target', 'size', 'created_at']
    list_filter = ['target', 'created_at']
    search_fields = ['filename', 'revision__commit_hash']
    readonly_fields = ['file_path', 'size', 'created_at']
    raw_id_fields = ['revision', 'target']
