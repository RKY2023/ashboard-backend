# Diary Entry Module

App: `dairyentry` (note the spelling — the Django app is `dairyentry`, but URLs are mounted under `diaryentry/`).

Mounted at:
- `/diaryentry/` (legacy)
- `/api/diaryentry/` (canonical, used by Swagger)

Implemented with DRF `ViewSet`s registered through `DefaultRouter`.

## Models (`dairyentry/models.py`)

| Model | Purpose |
|---|---|
| `DiaryEntry` | Main daily entry: title, content, mood, mood_score, weather, location, `entry_date`/`entry_time`, plus enhanced JSON fields (`health_status`, `productive_work_list`, `word_of_day`, `quote`). |
| `EventContent` | Time-stamped content items belonging to a `DiaryEntry` (multiple events per day with `event_datetime` + `order`). |
| `TimelineEvent` | Long-running event/period (milestone, project, travel, etc.) that groups diary entries. Supports parent/child via `parent_event`. |
| `TimelineCheckpoint` | Checkpoints/milestones inside a `TimelineEvent`. |
| `FoodRoutine` | Per-day meal tracking (`morning_items`, `breakfast_items`, `lunch_items`, `dinner_items`, `snacks` as JSON), `water_intake`, `total_calories`. Unique per `(user, date)`. |
| `Tag` | Shared tags for diary entries and timeline events. Unique per `(name, user)` — `user=null` means a global tag. |
| `Attachment` | File uploads on a diary entry (image/video/audio/document). |
| `DiaryEntryShare` | Share a diary entry with another user (read-only or comment). |

All user-owned models inherit from `commoninfo.models.CommonInfo` for `created_at`/`updated_at`.

## Endpoints

Registered routes (see `dairyentry/urls.py`):

| Resource | Path |
|---|---|
| Diary entries | `diary-entries/` |
| Timeline events | `timeline-events/` |
| Checkpoints | `checkpoints/` |
| Tags | `tags/` |
| Attachments | `attachments/` |
| Shares | `shares/` |
| Event contents | `event-contents/` |
| Food routines | `food-routines/` |

Each is a full ViewSet (list/create/retrieve/update/destroy).

## Swagger tags

The diary module is split across these `drf-spectacular` tags (see `SPECTACULAR_SETTINGS` in `blogs/settings.py`): `Diary Entry`, `Event Content`, `Food Routine`, `Timeline Events`, `Tags`.
