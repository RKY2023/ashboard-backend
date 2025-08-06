from django.db import models
from django.contrib.auth.models import User

class DiaryEntry(models.Model):
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
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=150, blank=True)
    content = models.TextField()
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, blank=True, null=True)
    mood_score = models.PositiveSmallIntegerField(null=True, blank=True)  # 1–10 scale
    tags = models.ManyToManyField('Tag', blank=True)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='private')
    weather = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title or 'Untitled'} - {self.created_at}"


class Attachment(models.Model):
    diary_entry = models.ForeignKey(DiaryEntry, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='diary_attachments/')
    file_type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment {self.id} for {self.diary_entry}"


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class DiaryEntryShare(models.Model):
    diary_entry = models.ForeignKey(DiaryEntry, on_delete=models.CASCADE)
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_diaries')
    permission = models.CharField(max_length=10, choices=[('read', 'Read'), ('comment', 'Comment')], default='read')
    shared_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('diary_entry', 'shared_with')

    def __str__(self):
        return f"{self.diary_entry} shared with {self.shared_with}"
