from django.contrib import admin
from .models import DiaryEntry, DiaryEntryShare, Attachment, Tag, TimelineEvent, TimelineCheckpoint, EventContent, FoodRoutine


@admin.register(TimelineEvent)
class TimelineEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'event_type', 'status', 'start_date', 'end_date', 'is_milestone']
    list_filter = ['event_type', 'status', 'is_milestone', 'is_private']
    search_fields = ['title', 'description']
    date_hierarchy = 'start_date'
    filter_horizontal = ['tags']


@admin.register(DiaryEntry)
class DiaryEntryAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'entry_date', 'mood', 'timeline_event', 'is_pinned', 'is_favorite', 'is_archived']
    list_filter = ['mood', 'visibility', 'is_pinned', 'is_favorite', 'is_archived']
    search_fields = ['title', 'content']
    date_hierarchy = 'entry_date'
    filter_horizontal = ['tags']


@admin.register(TimelineCheckpoint)
class TimelineCheckpointAdmin(admin.ModelAdmin):
    list_display = ['title', 'timeline_event', 'checkpoint_date', 'is_completed', 'completed_at']
    list_filter = ['is_completed']
    search_fields = ['title', 'description']
    date_hierarchy = 'checkpoint_date'


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['diary_entry', 'file_type', 'file_size', 'uploaded_at']
    list_filter = ['file_type']
    date_hierarchy = 'uploaded_at'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'color']
    list_filter = ['user']
    search_fields = ['name']


@admin.register(DiaryEntryShare)
class DiaryEntryShareAdmin(admin.ModelAdmin):
    list_display = ['diary_entry', 'shared_with', 'permission', 'shared_at']
    list_filter = ['permission']
    date_hierarchy = 'shared_at'


@admin.register(EventContent)
class EventContentAdmin(admin.ModelAdmin):
    list_display = ['diary_entry', 'event_datetime', 'order', 'created_at']
    list_filter = ['event_datetime']
    search_fields = ['event_content']
    date_hierarchy = 'event_datetime'
    ordering = ['diary_entry', 'event_datetime', 'order']


@admin.register(FoodRoutine)
class FoodRoutineAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'water_intake', 'total_calories', 'diary_entry', 'created_at']
    list_filter = ['date']
    search_fields = ['user__username', 'notes']
    date_hierarchy = 'date'
    ordering = ['-date']
    readonly_fields = ['created_at', 'updated_at']