from rest_framework import serializers
from .models import DiaryEntry, TimelineEvent, TimelineCheckpoint, Tag, Attachment, DiaryEntryShare, EventContent, FoodRoutine


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color']
        read_only_fields = ['id']

    def create(self, validated_data):
        """Set user from request context"""
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file', 'file_type', 'file_size', 'uploaded_at']
        read_only_fields = ['id', 'file_size', 'uploaded_at']


class EventContentSerializer(serializers.ModelSerializer):
    """Serializer for timeline-based event content"""
    class Meta:
        model = EventContent
        fields = [
            'id',
            'diary_entry',
            'event_datetime',
            'event_content',
            'order',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FoodRoutineListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing food routines"""
    has_morning = serializers.SerializerMethodField()
    has_breakfast = serializers.SerializerMethodField()
    has_lunch = serializers.SerializerMethodField()
    has_dinner = serializers.SerializerMethodField()

    class Meta:
        model = FoodRoutine
        fields = [
            'id',
            'date',
            'water_intake',
            'total_calories',
            'has_morning',
            'has_breakfast',
            'has_lunch',
            'has_dinner',
            'created_at'
        ]

    def get_has_morning(self, obj) -> bool:
        return bool(obj.morning_items)

    def get_has_breakfast(self, obj) -> bool:
        return bool(obj.breakfast_items)

    def get_has_lunch(self, obj) -> bool:
        return bool(obj.lunch_items)

    def get_has_dinner(self, obj) -> bool:
        return bool(obj.dinner_items)


class FoodRoutineSerializer(serializers.ModelSerializer):
    """Detailed serializer for food routines"""
    class Meta:
        model = FoodRoutine
        fields = [
            'id',
            'date',
            'morning_items',
            'breakfast_items',
            'lunch_items',
            'dinner_items',
            'snacks',
            'water_intake',
            'total_calories',
            'notes',
            'diary_entry',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Set user from request context"""
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class TimelineEventListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing timeline events"""
    tag_count = serializers.SerializerMethodField()
    diary_entry_count = serializers.SerializerMethodField()

    class Meta:
        model = TimelineEvent
        fields = [
            'id',
            'title',
            'event_type',
            'status',
            'start_date',
            'end_date',
            'color',
            'icon',
            'is_milestone',
            'tag_count',
            'diary_entry_count',
            'created_at'
        ]

    def get_tag_count(self, obj) -> int:
        return obj.tags.count()

    def get_diary_entry_count(self, obj) -> int:
        return obj.diary_entries.count()


class TimelineEventSerializer(serializers.ModelSerializer):
    """Detailed serializer for timeline events"""
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        source='tags',
        write_only=True,
        required=False
    )
    sub_events = TimelineEventListSerializer(many=True, read_only=True)
    checkpoint_count = serializers.SerializerMethodField()

    class Meta:
        model = TimelineEvent
        fields = [
            'id',
            'title',
            'description',
            'event_type',
            'status',
            'start_date',
            'end_date',
            'location',
            'color',
            'icon',
            'tags',
            'tag_ids',
            'parent_event',
            'sub_events',
            'is_private',
            'is_milestone',
            'checkpoint_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_checkpoint_count(self, obj) -> int:
        return obj.checkpoints.count()

    def create(self, validated_data):
        """Set user from request context"""
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class TimelineCheckpointSerializer(serializers.ModelSerializer):
    diary_entry_title = serializers.CharField(source='diary_entry.title', read_only=True)

    class Meta:
        model = TimelineCheckpoint
        fields = [
            'id',
            'timeline_event',
            'title',
            'description',
            'checkpoint_date',
            'is_completed',
            'completed_at',
            'diary_entry',
            'diary_entry_title',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DiaryEntryListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing diary entries"""
    timeline_event_title = serializers.CharField(source='timeline_event.title', read_only=True)
    tag_count = serializers.SerializerMethodField()
    attachment_count = serializers.SerializerMethodField()
    event_content_count = serializers.SerializerMethodField()
    has_food_routine = serializers.SerializerMethodField()

    class Meta:
        model = DiaryEntry
        fields = [
            'id',
            'title',
            'entry_date',
            'mood',
            'mood_score',
            'word_of_day',
            'timeline_event_title',
            'is_pinned',
            'is_favorite',
            'is_archived',
            'tag_count',
            'attachment_count',
            'event_content_count',
            'has_food_routine',
            'created_at'
        ]

    def get_tag_count(self, obj) -> int:
        return obj.tags.count()

    def get_attachment_count(self, obj) -> int:
        return obj.attachments.count()

    def get_event_content_count(self, obj) -> int:
        return obj.event_contents.count()

    def get_has_food_routine(self, obj) -> bool:
        return hasattr(obj, 'food_routine') and obj.food_routine is not None


class DiaryEntrySerializer(serializers.ModelSerializer):
    """Detailed serializer for diary entries"""
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        source='tags',
        write_only=True,
        required=False
    )
    attachments = AttachmentSerializer(many=True, read_only=True)
    timeline_event_title = serializers.CharField(source='timeline_event.title', read_only=True)
    checkpoints = TimelineCheckpointSerializer(many=True, read_only=True)
    event_contents = EventContentSerializer(many=True, read_only=True)
    food_routine = FoodRoutineSerializer(read_only=True)

    class Meta:
        model = DiaryEntry
        fields = [
            'id',
            'title',
            'content',
            'mood',
            'mood_score',
            'tags',
            'tag_ids',
            'visibility',
            'weather',
            'location',
            'timeline_event',
            'timeline_event_title',
            'entry_date',
            'entry_time',
            'word_of_day',
            'quote',
            'health_status',
            'productive_work_list',
            'is_pinned',
            'is_favorite',
            'is_archived',
            'attachments',
            'checkpoints',
            'event_contents',
            'food_routine',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Set user from request context"""
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class DiaryEntryShareSerializer(serializers.ModelSerializer):
    diary_entry_title = serializers.CharField(source='diary_entry.title', read_only=True)
    shared_with_username = serializers.CharField(source='shared_with.username', read_only=True)

    class Meta:
        model = DiaryEntryShare
        fields = [
            'id',
            'diary_entry',
            'diary_entry_title',
            'shared_with',
            'shared_with_username',
            'permission',
            'shared_at',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'shared_at', 'created_at', 'updated_at']
