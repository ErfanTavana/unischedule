from datetime import date

from django.test import TestCase

from institutions.models import Institution
from semesters.models import Semester
from semesters.services import semester_service


class SemesterServiceTests(TestCase):
    """Integration style tests covering the public semester service helpers."""

    def setUp(self):
        """Create a reusable institution instance for each scenario."""
        self.institution = Institution.objects.create(name="Test University", slug="test-university")

    def test_create_semester_deactivates_existing_active(self):
        """Creating an active semester should deactivate other active records."""

        first_semester = Semester.objects.create(
            institution=self.institution,
            title="Spring 2023",
            start_date=date(2023, 1, 1),
            end_date=date(2023, 6, 1),
            is_active=True,
        )

        payload = {
            "title": "Fall 2023",
            "start_date": date(2023, 9, 1),
            "end_date": date(2024, 1, 1),
            "is_active": True,
        }

        semester_service.create_semester(payload, self.institution)

        first_semester.refresh_from_db()
        self.assertFalse(first_semester.is_active, "The previously active semester should be deactivated.")

    def test_update_semester_enforces_single_active(self):
        """Updating a semester to active must turn off the other semester."""

        inactive_semester = Semester.objects.create(
            institution=self.institution,
            title="Spring 2024",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 1),
            is_active=False,
        )
        active_semester = Semester.objects.create(
            institution=self.institution,
            title="Summer 2024",
            start_date=date(2024, 6, 2),
            end_date=date(2024, 9, 1),
            is_active=True,
        )

        semester_service.update_semester(inactive_semester, {"is_active": True})

        active_semester.refresh_from_db()
        inactive_semester.refresh_from_db()
        self.assertTrue(inactive_semester.is_active, "The updated semester should be marked active.")
        self.assertFalse(active_semester.is_active, "The previously active semester must be deactivated.")

    def test_set_active_semester_helper(self):
        """The explicit helper should activate the provided semester only."""

        first_semester = Semester.objects.create(
            institution=self.institution,
            title="Winter 2024",
            start_date=date(2024, 12, 1),
            end_date=date(2025, 2, 28),
            is_active=False,
        )
        second_semester = Semester.objects.create(
            institution=self.institution,
            title="Spring 2025",
            start_date=date(2025, 3, 1),
            end_date=date(2025, 7, 1),
            is_active=True,
        )

        semester_service.set_active_semester(first_semester)

        first_semester.refresh_from_db()
        second_semester.refresh_from_db()
        self.assertTrue(first_semester.is_active, "The selected semester should become active.")
        self.assertFalse(second_semester.is_active, "All other semesters must be inactive after the change.")
