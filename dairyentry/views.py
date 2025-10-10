from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q, Count, Prefetch
from datetime import datetime
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import DiaryEntry, DiaryEntryShare, Attachment, Tag, TimelineEvent, TimelineCheckpoint, EventContent, FoodRoutine
from .serializers import (
    DiaryEntrySerializer,
    DiaryEntryListSerializer,
    TimelineEventSerializer,
    TimelineEventListSerializer,
    TimelineCheckpointSerializer,
    TagSerializer,
    AttachmentSerializer,
    DiaryEntryShareSerializer,
    EventContentSerializer,
    FoodRoutineSerializer,
    FoodRoutineListSerializer
)


@extend_schema_view(
    list=extend_schema(
        summary="List Diary Entries",
        description="Retrieve a list of all diary entries for the authenticated user. Supports filtering, searching, and ordering.",
        tags=['Diary Entry'],
    ),
    retrieve=extend_schema(
        summary="Get Diary Entry",
        description="Retrieve detailed information about a specific diary entry including event contents, food routine, and attachments.",
        tags=['Diary Entry'],
    ),
    create=extend_schema(
        summary="Create Diary Entry",
        description="Create a new diary entry with optional fields like mood, word of day, quote, health status, and productive work list.",
        tags=['Diary Entry'],
    ),
    update=extend_schema(
        summary="Update Diary Entry",
        description="Update an existing diary entry completely.",
        tags=['Diary Entry'],
    ),
    partial_update=extend_schema(
        summary="Partial Update Diary Entry",
        description="Partially update specific fields of a diary entry.",
        tags=['Diary Entry'],
    ),
    destroy=extend_schema(
        summary="Delete Diary Entry",
        description="Delete a diary entry permanently.",
        tags=['Diary Entry'],
    ),
)
class DiaryEntryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing diary entries.
    Supports filtering by date, mood, tags, and timeline events.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['mood', 'visibility', 'is_pinned', 'is_favorite', 'is_archived', 'timeline_event']
    search_fields = ['title', 'content']
    ordering_fields = ['entry_date', 'created_at', 'mood_score']
    ordering = ['-entry_date', '-created_at']

    def get_queryset(self):
        """Filter diary entries by current user and prefetch related data"""
        return DiaryEntry.objects.filter(
            user=self.request.user
        ).prefetch_related('tags', 'attachments', 'event_contents').select_related('timeline_event', 'food_routine')

    def get_serializer_class(self):
        """Use list serializer for list action, detailed for others"""
        if self.action == 'list':
            return DiaryEntryListSerializer
        return DiaryEntrySerializer

    @extend_schema(
        summary="Get Diary Entries by Date Range",
        description="Filter diary entries within a specific date range.",
        parameters=[
            OpenApiParameter(name='start_date', type=OpenApiTypes.DATE, required=True, description='Start date (YYYY-MM-DD)'),
            OpenApiParameter(name='end_date', type=OpenApiTypes.DATE, required=True, description='End date (YYYY-MM-DD)'),
        ],
        tags=['Diary Entry'],
    )
    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        """Get diary entries within a date range"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return Response({
                'error': 'Both start_date and end_date are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset().filter(
            entry_date__range=[start_date, end_date]
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get Pinned Diary Entries",
        description="Retrieve all pinned diary entries (excluding archived ones).",
        tags=['Diary Entry'],
    )
    @action(detail=False, methods=['get'])
    def pinned(self, request):
        """Get pinned diary entries"""
        queryset = self.get_queryset().filter(is_pinned=True, is_archived=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get Favorite Diary Entries",
        description="Retrieve all favorite diary entries (excluding archived ones).",
        tags=['Diary Entry'],
    )
    @action(detail=False, methods=['get'])
    def favorites(self, request):
        """Get favorite diary entries"""
        queryset = self.get_queryset().filter(is_favorite=True, is_archived=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Toggle Pin Status",
        description="Toggle the pinned status of a diary entry.",
        tags=['Diary Entry'],
    )
    @action(detail=True, methods=['post'])
    def toggle_pin(self, request, pk=None):
        """Toggle pinned status"""
        entry = self.get_object()
        entry.is_pinned = not entry.is_pinned
        entry.save()
        return Response({'is_pinned': entry.is_pinned})

    @extend_schema(
        summary="Toggle Favorite Status",
        description="Toggle the favorite status of a diary entry.",
        tags=['Diary Entry'],
    )
    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """Toggle favorite status"""
        entry = self.get_object()
        entry.is_favorite = not entry.is_favorite
        entry.save()
        return Response({'is_favorite': entry.is_favorite})

    @extend_schema(
        summary="Archive Diary Entry",
        description="Mark a diary entry as archived.",
        tags=['Diary Entry'],
    )
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a diary entry"""
        entry = self.get_object()
        entry.is_archived = True
        entry.save()
        return Response({'message': 'Diary entry archived'})

    @extend_schema(
        summary="Unarchive Diary Entry",
        description="Remove archived status from a diary entry.",
        tags=['Diary Entry'],
    )
    @action(detail=True, methods=['post'])
    def unarchive(self, request, pk=None):
        """Unarchive a diary entry"""
        entry = self.get_object()
        entry.is_archived = False
        entry.save()
        return Response({'message': 'Diary entry unarchived'})


class TimelineEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing timeline events.
    Supports filtering by event type, status, and date ranges.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event_type', 'status', 'is_milestone', 'is_private', 'parent_event']
    search_fields = ['title', 'description']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-start_date', '-created_at']

    def get_queryset(self):
        """Filter timeline events by current user and prefetch related data"""
        return TimelineEvent.objects.filter(
            user=self.request.user
        ).prefetch_related('tags', 'sub_events', 'checkpoints').select_related('parent_event')

    def get_serializer_class(self):
        """Use list serializer for list action, detailed for others"""
        if self.action == 'list':
            return TimelineEventListSerializer
        return TimelineEventSerializer

    @action(detail=False, methods=['get'])
    def ongoing(self, request):
        """Get ongoing timeline events"""
        queryset = self.get_queryset().filter(status='ongoing')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def milestones(self, request):
        """Get milestone events"""
        queryset = self.get_queryset().filter(is_milestone=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def diary_entries(self, request, pk=None):
        """Get all diary entries for this timeline event"""
        timeline_event = self.get_object()
        entries = timeline_event.diary_entries.all().order_by('-entry_date')
        serializer = DiaryEntryListSerializer(entries, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark timeline event as completed"""
        event = self.get_object()
        event.status = 'completed'
        if not event.end_date:
            event.end_date = datetime.now().date()
        event.save()
        return Response({'message': 'Timeline event marked as completed'})


class TimelineCheckpointViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing timeline checkpoints.
    """
    serializer_class = TimelineCheckpointSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['timeline_event', 'is_completed']
    ordering_fields = ['checkpoint_date', 'created_at']
    ordering = ['checkpoint_date']

    def get_queryset(self):
        """Filter checkpoints by user's timeline events"""
        return TimelineCheckpoint.objects.filter(
            timeline_event__user=self.request.user
        ).select_related('timeline_event', 'diary_entry')

    @action(detail=True, methods=['post'])
    def toggle_complete(self, request, pk=None):
        """Toggle checkpoint completion status"""
        checkpoint = self.get_object()
        checkpoint.is_completed = not checkpoint.is_completed
        if checkpoint.is_completed:
            checkpoint.completed_at = datetime.now()
        else:
            checkpoint.completed_at = None
        checkpoint.save()
        return Response({
            'is_completed': checkpoint.is_completed,
            'completed_at': checkpoint.completed_at
        })


class TagViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tags.
    """
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering = ['name']

    def get_queryset(self):
        """Get user-specific tags and global tags"""
        return Tag.objects.filter(
            Q(user=self.request.user) | Q(user__isnull=True)
        )


class AttachmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing attachments.
    """
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['diary_entry', 'file_type']

    def get_queryset(self):
        """Filter attachments by user's diary entries"""
        return Attachment.objects.filter(
            diary_entry__user=self.request.user
        ).select_related('diary_entry')


class DiaryEntryShareViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing diary entry shares.
    """
    serializer_class = DiaryEntryShareSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['permission']

    def get_queryset(self):
        """Get shares for current user's diary entries"""
        return DiaryEntryShare.objects.filter(
            diary_entry__user=self.request.user
        ).select_related('diary_entry', 'shared_with')


@extend_schema_view(
    list=extend_schema(
        summary="List Event Contents",
        description="Retrieve timeline-based event contents for diary entries. Filter by diary_entry to get events for a specific entry.",
        tags=['Event Content'],
    ),
    retrieve=extend_schema(
        summary="Get Event Content",
        description="Retrieve details of a specific event content entry.",
        tags=['Event Content'],
    ),
    create=extend_schema(
        summary="Create Event Content",
        description="Add a new time-stamped event to a diary entry.",
        tags=['Event Content'],
    ),
    update=extend_schema(
        summary="Update Event Content",
        description="Update an existing event content entry.",
        tags=['Event Content'],
    ),
    partial_update=extend_schema(
        summary="Partial Update Event Content",
        description="Partially update an event content entry.",
        tags=['Event Content'],
    ),
    destroy=extend_schema(
        summary="Delete Event Content",
        description="Delete an event content entry.",
        tags=['Event Content'],
    ),
)
class EventContentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing event contents (timeline-based diary content).
    """
    serializer_class = EventContentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['diary_entry']
    ordering_fields = ['event_datetime', 'order', 'created_at']
    ordering = ['event_datetime', 'order']

    def get_queryset(self):
        """Filter event contents by user's diary entries"""
        return EventContent.objects.filter(
            diary_entry__user=self.request.user
        ).select_related('diary_entry')


@extend_schema_view(
    list=extend_schema(
        summary="List Food Routines",
        description="Retrieve a list of food routines for the authenticated user. Supports filtering by date.",
        tags=['Food Routine'],
    ),
    retrieve=extend_schema(
        summary="Get Food Routine",
        description="Retrieve detailed information about a specific food routine including all meals and nutrition data.",
        tags=['Food Routine'],
    ),
    create=extend_schema(
        summary="Create Food Routine",
        description="Create a new daily food routine with meals, snacks, and nutrition tracking.",
        tags=['Food Routine'],
    ),
    update=extend_schema(
        summary="Update Food Routine",
        description="Update an existing food routine completely.",
        tags=['Food Routine'],
    ),
    partial_update=extend_schema(
        summary="Partial Update Food Routine",
        description="Partially update specific fields of a food routine.",
        tags=['Food Routine'],
    ),
    destroy=extend_schema(
        summary="Delete Food Routine",
        description="Delete a food routine permanently.",
        tags=['Food Routine'],
    ),
)
class FoodRoutineViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing food routines.
    Supports filtering by date ranges.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['date', 'diary_entry']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date']

    def get_queryset(self):
        """Filter food routines by current user"""
        return FoodRoutine.objects.filter(
            user=self.request.user
        ).select_related('diary_entry')

    def get_serializer_class(self):
        """Use list serializer for list action, detailed for others"""
        if self.action == 'list':
            return FoodRoutineListSerializer
        return FoodRoutineSerializer

    @extend_schema(
        summary="Get Food Routines by Date Range",
        description="Filter food routines within a specific date range.",
        parameters=[
            OpenApiParameter(name='start_date', type=OpenApiTypes.DATE, required=True, description='Start date (YYYY-MM-DD)'),
            OpenApiParameter(name='end_date', type=OpenApiTypes.DATE, required=True, description='End date (YYYY-MM-DD)'),
        ],
        tags=['Food Routine'],
    )
    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        """Get food routines within a date range"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return Response({
                'error': 'Both start_date and end_date are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset().filter(
            date__range=[start_date, end_date]
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get Today's Food Routine",
        description="Retrieve the food routine for the current date.",
        tags=['Food Routine'],
    )
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's food routine"""
        today = datetime.now().date()
        try:
            routine = self.get_queryset().get(date=today)
            serializer = self.get_serializer(routine)
            return Response(serializer.data)
        except FoodRoutine.DoesNotExist:
            return Response({
                'message': 'No food routine found for today'
            }, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Get Weekly Food Summary",
        description="Retrieve a summary of food routines for the current week (Monday to Sunday).",
        tags=['Food Routine'],
    )
    @action(detail=False, methods=['get'])
    def weekly_summary(self, request):
        """Get summary of food routines for the current week"""
        from datetime import timedelta
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        queryset = self.get_queryset().filter(
            date__range=[week_start, week_end]
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'week_start': week_start,
            'week_end': week_end,
            'routines': serializer.data
        })
