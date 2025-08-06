from django.contrib import admin
from .models import DiaryEntry, DiaryEntryShare, Attachment, Tag

# Register your models here.
admin.site.register(DiaryEntry)
admin.site.register(DiaryEntryShare)
admin.site.register(Attachment)
admin.site.register(Tag)