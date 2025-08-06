from django.shortcuts import render
from rest_framework.views import APIView as ApiView
from rest_framework.response import Response

from .models import DiaryEntry, DiaryEntryShare, Attachment, Tag
from user.models import User

# Create your views here.
class DiaryEntryView(ApiView):
    def get(self, request):
        entries = DiaryEntry.objects.all()
        data = list(entries.values())
        return render(request, 'dairyentry/diaryentry_list.html', {'entries': data})

    def post(self, request):
        title = request.data.get('title')
        content = request.data.get('content')
        if title and content:
            entry = DiaryEntry.objects.create(title=title, content=content)
            return Response({'message': 'Diary entry created successfully', 'entry_id': entry.id})
        return Response({'error': 'Invalid data'}, status=400)
class DiaryEntryShareView(ApiView):
    def post(self, request):
        diary_entry_id = request.data.get('diary_entry_id')
        shared_with_id = request.data.get('shared_with_id')
        permission = request.data.get('permission', 'read')

        if diary_entry_id and shared_with_id:
            diary_entry = DiaryEntry.objects.get(id=diary_entry_id)
            shared_with = User.objects.get(id=shared_with_id)
            share = DiaryEntryShare.objects.create(diary_entry=diary_entry, shared_with=shared_with, permission=permission)
            return Response({'message': 'Diary entry shared successfully', 'share_id': share.id})
        return Response({'error': 'Invalid data'}, status=400)
