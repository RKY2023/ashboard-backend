from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DiaryEntryViewSet,
    TimelineEventViewSet,
    TimelineCheckpointViewSet,
    TagViewSet,
    AttachmentViewSet,
    DiaryEntryShareViewSet,
    EventContentViewSet,
    FoodRoutineViewSet
)

router = DefaultRouter()
router.register(r'diary-entries', DiaryEntryViewSet, basename='diary-entry')
router.register(r'timeline-events', TimelineEventViewSet, basename='timeline-event')
router.register(r'checkpoints', TimelineCheckpointViewSet, basename='checkpoint')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'attachments', AttachmentViewSet, basename='attachment')
router.register(r'shares', DiaryEntryShareViewSet, basename='share')
router.register(r'event-contents', EventContentViewSet, basename='event-content')
router.register(r'food-routines', FoodRoutineViewSet, basename='food-routine')

urlpatterns = [
    path('', include(router.urls)),
]