from django.db import models
from django.conf import settings
from django.utils import timezone
from commoninfo.models import CommonInfo


class TimelineEvent(CommonInfo):
    """
    Timeline events represent significant moments, milestones, or periods
    that can group multiple diary entries together
    """
    EVENT_TYPE_CHOICES = [
        ('milestone', 'Milestone'),
        ('project', 'Project'),
        ('travel', 'Travel'),
        ('relationship', 'Relationship'),
        ('health', 'Health'),
        ('education', 'Education'),
        ('career', 'Career'),
        ('personal', 'Personal'),
        ('goal', 'Goal'),
        ('habit', 'Habit'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='timeline_events'
    )

    # Basic info
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ongoing')

    # Temporal range
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True, help_text="Leave blank for ongoing events")

    # Location & context
    location = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=7, default='#3B82F6', help_text="Hex color for timeline visualization")
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Icon/emoji for UI")

    # Metadata
    tags = models.ManyToManyField('Tag', blank=True, related_name='timeline_events')

    # Parent-child for nested timelines
    parent_event = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sub_events'
    )

    # Flags
    is_private = models.BooleanField(default=True)
    is_milestone = models.BooleanField(default=False, help_text="Mark as major milestone")

    class Meta:
        ordering = ['-start_date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'start_date']),
            models.Index(fields=['user', 'event_type']),
            models.Index(fields=['status']),
            models.Index(fields=['parent_event']),
        ]

    def __str__(self):
        return f"{self.title} ({self.start_date})"


class DiaryEntry(CommonInfo):
    """
    Main diary entry model with timeline support and enhanced daily tracking
    """
    VISIBILITY_CHOICES = [
        ('private', 'Private'),
        ('public', 'Public'),
        ('friends', 'Friends Only'),
    ]

    MOOD_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
        ('anxious', 'Anxious'),
        ('neutral', 'Neutral'),
        ('excited', 'Excited'),
        ('tired', 'Tired'),
        ('productive', 'Productive'),
        ('grateful', 'Grateful'),
        ('reflective', 'Reflective'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='diary_entries'
    )
    title = models.CharField(max_length=150, blank=True)
    content = models.TextField(blank=True, null=True, help_text="Legacy content field - use EventContent for timeline-based entries")

    # Mood tracking
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, blank=True, null=True)
    mood_score = models.PositiveSmallIntegerField(null=True, blank=True, help_text="1-10 scale")

    # Metadata
    tags = models.ManyToManyField('Tag', blank=True, related_name='diary_entries')
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='private')
    weather = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    # Timeline association
    timeline_event = models.ForeignKey(
        TimelineEvent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='diary_entries',
        help_text="Optional timeline event this diary entry belongs to"
    )

    # Temporal data
    entry_date = models.DateField(default=timezone.now, help_text="The date this entry is about")
    entry_time = models.TimeField(blank=True, null=True, help_text="Specific time of day for the entry")

    # New Enhanced Fields
    word_of_day = models.CharField(max_length=100, blank=True, null=True, help_text="Interesting word learned today")
    quote = models.TextField(blank=True, null=True, help_text="Inspiring quote of the day")
    health_status = models.JSONField(
        blank=True,
        null=True,
        help_text="Health tracking: sleep_hours, exercise_minutes, energy_level, symptoms, etc."
    )
    productive_work_list = models.JSONField(
        blank=True,
        null=True,
        help_text="List of productive tasks/accomplishments for the day"
    )

    # Flags
    is_pinned = models.BooleanField(default=False, help_text="Pin important entries")
    is_favorite = models.BooleanField(default=False, help_text="Mark as favorite")
    is_archived = models.BooleanField(default=False, help_text="Archive old entries")

    class Meta:
        ordering = ['-entry_date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'entry_date']),
            models.Index(fields=['user', 'is_pinned', 'is_archived']),
            models.Index(fields=['mood']),
            models.Index(fields=['timeline_event']),
        ]
        verbose_name_plural = 'Diary Entries'

    def __str__(self):
        return f"{self.title or 'Untitled'} - {self.entry_date}"


class EventContent(CommonInfo):
    """
    Timeline-based content entries for a diary entry
    Allows multiple time-stamped content pieces per day
    """
    diary_entry = models.ForeignKey(
        DiaryEntry,
        on_delete=models.CASCADE,
        related_name='event_contents'
    )
    event_datetime = models.DateTimeField(help_text="Date and time when this event occurred")
    event_content = models.TextField(help_text="Content/description of what happened at this time")
    order = models.PositiveIntegerField(default=0, help_text="Display order within the diary entry")

    class Meta:
        ordering = ['diary_entry', 'event_datetime', 'order']
        indexes = [
            models.Index(fields=['diary_entry', 'event_datetime']),
            models.Index(fields=['diary_entry', 'order']),
        ]
        verbose_name_plural = 'Event Contents'

    def __str__(self):
        return f"{self.diary_entry.title} - {self.event_datetime.strftime('%H:%M')}"


class FoodRoutine(CommonInfo):
    """
    Daily food routine tracking module
    Tracks meals and nutrition throughout the day
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='food_routines'
    )
    date = models.DateField(default=timezone.now, help_text="Date of this food routine")

    # Meal tracking (each as JSONField for flexibility)
    morning_items = models.JSONField(
        blank=True,
        null=True,
        help_text="Morning food/drinks: [{name, quantity, time, calories, notes}, ...]"
    )
    breakfast_items = models.JSONField(
        blank=True,
        null=True,
        help_text="Breakfast items: [{name, quantity, time, calories, notes}, ...]"
    )
    lunch_items = models.JSONField(
        blank=True,
        null=True,
        help_text="Lunch items: [{name, quantity, time, calories, notes}, ...]"
    )
    dinner_items = models.JSONField(
        blank=True,
        null=True,
        help_text="Dinner items: [{name, quantity, time, calories, notes}, ...]"
    )
    snacks = models.JSONField(
        blank=True,
        null=True,
        help_text="Snacks throughout the day: [{name, quantity, time, calories, notes}, ...]"
    )

    # Additional tracking
    water_intake = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Water intake in liters"
    )
    total_calories = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Estimated total calories for the day"
    )
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about food routine")

    # Optional link to diary entry
    diary_entry = models.OneToOneField(
        DiaryEntry,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='food_routine',
        help_text="Optional link to diary entry for this day"
    )

    class Meta:
        ordering = ['-date', '-created_at']
        unique_together = ('user', 'date')
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['date']),
        ]
        verbose_name_plural = 'Food Routines'

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class TimelineCheckpoint(CommonInfo):
    """
    Checkpoints/milestones within a timeline event
    """
    timeline_event = models.ForeignKey(
        TimelineEvent,
        on_delete=models.CASCADE,
        related_name='checkpoints'
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    checkpoint_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    # Optional diary entry linked to this checkpoint
    diary_entry = models.ForeignKey(
        DiaryEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='checkpoints'
    )

    class Meta:
        ordering = ['checkpoint_date']
        indexes = [
            models.Index(fields=['timeline_event', 'checkpoint_date']),
        ]

    def __str__(self):
        return f"{self.title} - {self.checkpoint_date}"


class Attachment(models.Model):
    """
    Attachments for diary entries (images, PDFs, etc.)
    """
    ATTACHMENT_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
        ('other', 'Other'),
    ]

    diary_entry = models.ForeignKey(
        DiaryEntry,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(upload_to='diary_attachments/%Y/%m/')
    file_type = models.CharField(max_length=20, choices=ATTACHMENT_TYPE_CHOICES)
    file_size = models.PositiveIntegerField(help_text="File size in bytes", default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_type} for {self.diary_entry}"


class Tag(models.Model):
    """
    Shared tags for both diary entries and timeline events
    """
    name = models.CharField(max_length=50)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="User-specific tag (null for global tags)"
    )
    color = models.CharField(max_length=7, blank=True, null=True, help_text="Hex color")

    class Meta:
        unique_together = ('name', 'user')
        ordering = ['name']

    def __str__(self):
        return self.name


class DiaryEntryShare(models.Model):
    """
    Share diary entries with specific users
    """
    PERMISSION_CHOICES = [
        ('read', 'Read Only'),
        ('comment', 'Can Comment'),
    ]

    diary_entry = models.ForeignKey(
        DiaryEntry,
        on_delete=models.CASCADE,
        related_name='shares'
    )
    shared_with = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shared_diaries'
    )
    permission = models.CharField(max_length=10, choices=PERMISSION_CHOICES, default='read')
    shared_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('diary_entry', 'shared_with')

    def __str__(self):
        return f"{self.diary_entry.title} shared with {self.shared_with.username}"
