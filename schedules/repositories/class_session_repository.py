from django.db.models import Q
from schedules.models import ClassSession


def create_class_session(data: dict) -> ClassSession:
    return ClassSession.objects.create(**data)


def get_class_session_by_id_and_institution(session_id: int, institution) -> ClassSession | None:
    return ClassSession.objects.filter(id=session_id, institution=institution, is_deleted=False).first()


def list_class_sessions_by_institution(institution):
    return ClassSession.objects.filter(institution=institution, is_deleted=False).order_by("-created_at")


def update_class_session_fields(session: ClassSession, fields: dict) -> ClassSession:
    for key, value in fields.items():
        setattr(session, key, value)
    session.save()
    return session


def soft_delete_class_session(session: ClassSession) -> None:
    session.is_deleted = True
    session.save()


def has_time_conflict(*, institution, semester, day_of_week, start_time, end_time, week_type, classroom, professor, exclude_id: int | None = None) -> bool:
    qs = ClassSession.objects.filter(
        institution=institution,
        semester=semester,
        day_of_week=day_of_week,
        is_deleted=False,
    )
    if exclude_id:
        qs = qs.exclude(id=exclude_id)

    if week_type != ClassSession.WeekTypeChoices.EVERY:
        qs = qs.filter(Q(week_type=ClassSession.WeekTypeChoices.EVERY) | Q(week_type=week_type))
    time_overlap = Q(start_time__lt=end_time) & Q(end_time__gt=start_time)
    return qs.filter(time_overlap).filter(Q(classroom=classroom) | Q(professor=professor)).exists()
