from django.urls import path
from .views import DiaryEntryView, DiaryEntryShareView, AttachmentView, TagView

urlpatterns = [
    path('diary-entries/', DiaryEntryView.as_view(), name='diary-entry-list'),
    path('diary-entries/share/', DiaryEntryShareView.as_view(), name='diary-entry-share'),
    path('attachments/', AttachmentView.as_view(), name='attachment-list'),
    path('tags/', TagView.as_view(), name='tag-list'),
]