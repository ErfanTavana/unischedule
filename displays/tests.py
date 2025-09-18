from __future__ import annotations

from datetime import date, time

from django.contrib.admin.sites import AdminSite
from django.http import HttpResponseRedirect
from django.test import RequestFactory, TestCase
from rest_framework.test import APIClient

from accounts.models import User
from courses.models import Course
from displays.admin import DisplayScreenAdmin
from displays.models import DisplayScreen
from displays.services import display_service
from institutions.models import Institution
from locations.models import Building, Classroom
from professors.models import Professor
from schedules.models import ClassSession
from semesters.models import Semester
from unischedule.core.exceptions import CustomValidationError


class DisplayServiceViewAdminTests(TestCase):
    maxDiff = None

    def setUp(self):
        self.institution = Institution.objects.create(name="Inst", slug="inst")
        self.other_institution = Institution.objects.create(name="Other", slug="other")
        self.user = User.objects.create_user(
            username="displays",
            password="pass",
            institution=self.institution,
        )
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.user)

        self.professor = Professor.objects.create(
            institution=self.institution,
            first_name="Ali",
            last_name="Ahmadi",
            national_code="1234567890",
        )
        self.other_professor = Professor.objects.create(
            institution=self.other_institution,
            first_name="Sara",
            last_name="Karimi",
            national_code="9876543210",
        )
        self.course = Course.objects.create(
            institution=self.institution,
            code="C1",
            title="Algorithms",
            professor=self.professor,
            offer_code="ALG-1",
            unit_count=3,
        )
        self.semester = Semester.objects.create(
            institution=self.institution,
            title="Fall",
            start_date=date(2024, 9, 1),
            end_date=date(2025, 1, 20),
        )
        self.building = Building.objects.create(title="Main", institution=self.institution)
        self.classroom = Classroom.objects.create(title="101", building=self.building)

        self.screen = DisplayScreen.objects.create(institution=self.institution, title="Lobby")

    def _create_session(self, **overrides) -> ClassSession:
        data = dict(
            institution=self.institution,
            course=self.course,
            professor=self.professor,
            classroom=self.classroom,
            semester=self.semester,
            day_of_week="شنبه",
            start_time=time(8, 0),
            end_time=time(10, 0),
            week_type=ClassSession.WeekTypeChoices.EVERY,
        )
        data.update(overrides)
        return ClassSession.objects.create(**data)

    def _set_screen_filters(self, filters: list[dict]):
        display_service.update_display_screen(self.screen, {"filters": filters})
        self.screen.refresh_from_db()

    def test_service_generates_payload_with_classroom_filter(self):
        self._create_session()
        self._set_screen_filters(
            [
                {
                    "classroom": self.classroom.id,
                    "day_of_week": "شنبه",
                    "position": 1,
                    "is_active": True,
                }
            ]
        )

        payload = display_service.build_public_payload(self.screen, use_cache=False)

        self.assertIn("sessions", payload)
        self.assertEqual(len(payload["sessions"]), 1)
        self.assertEqual(payload["sessions"][0]["classroom_title"], self.classroom.title)

    def test_service_filters_by_professor_and_week_type(self):
        odd_session = self._create_session(week_type=ClassSession.WeekTypeChoices.ODD)
        every_session = self._create_session(week_type=ClassSession.WeekTypeChoices.EVERY, start_time=time(10, 0))
        self._create_session(week_type=ClassSession.WeekTypeChoices.EVEN, start_time=time(12, 0))

        self._set_screen_filters(
            [
                {
                    "professor": self.professor.id,
                    "week_type": ClassSession.WeekTypeChoices.ODD,
                }
            ]
        )

        sessions = display_service.build_public_payload(self.screen, use_cache=False)["sessions"]
        session_ids = {session["id"] for session in sessions}
        self.assertIn(odd_session.id, session_ids)
        self.assertIn(every_session.id, session_ids)
        self.assertEqual(len(session_ids), 2)

    def test_filter_validation_rejects_foreign_institution(self):
        with self.assertRaises(CustomValidationError):
            self._set_screen_filters([
                {
                    "professor": self.other_professor.id,
                }
            ])

    def test_api_requires_authentication(self):
        unauthenticated = APIClient()
        response = unauthenticated.get("/api/displays/screens/")
        self.assertEqual(response.status_code, 401)

    def test_api_screen_and_filter_flow(self):
        screen_response = self.api_client.post(
            "/api/displays/screens/create/",
            {
                "title": "Hall",
                "refresh_interval": 45,
                "layout_theme": "dark",
                "filters": [
                    {
                        "classroom": self.classroom.id,
                        "semester": self.semester.id,
                        "day_of_week": "شنبه",
                        "position": 2,
                    }
                ],
            },
            format="json",
        )
        self.assertEqual(screen_response.status_code, 201)
        screen_data = screen_response.data["data"]["screen"]
        screen_id = screen_data["id"]
        self.assertEqual(len(screen_data["filters"]), 1)
        created_filter = screen_data["filters"][0]
        self.assertEqual(created_filter["display_screen"], screen_id)
        self.assertEqual(created_filter["classroom"], self.classroom.id)

        update_response = self.api_client.put(
            f"/api/displays/screens/{screen_id}/update/",
            {
                "filters": [
                    {
                        "id": created_filter["id"],
                        "classroom": self.classroom.id,
                        "semester": self.semester.id,
                        "day_of_week": "شنبه",
                        "week_type": ClassSession.WeekTypeChoices.EVERY,
                        "position": 1,
                    },
                    {
                        "title": "Professor filter",
                        "professor": self.professor.id,
                        "week_type": ClassSession.WeekTypeChoices.ODD,
                        "position": 2,
                    },
                ]
            },
            format="json",
        )
        self.assertEqual(update_response.status_code, 200)
        updated_filters = update_response.data["data"]["screen"]["filters"]
        self.assertEqual(len(updated_filters), 2)
        updated_ids = {flt["id"] for flt in updated_filters}
        self.assertIn(created_filter["id"], updated_ids)

        removal_response = self.api_client.put(
            f"/api/displays/screens/{screen_id}/update/",
            {
                "filters": [
                    {
                        "id": created_filter["id"],
                        "classroom": self.classroom.id,
                        "semester": self.semester.id,
                        "day_of_week": "شنبه",
                        "week_type": ClassSession.WeekTypeChoices.EVERY,
                        "position": 3,
                    }
                ]
            },
            format="json",
        )
        self.assertEqual(removal_response.status_code, 200)
        final_filters = removal_response.data["data"]["screen"]["filters"]
        self.assertEqual(len(final_filters), 1)
        self.assertEqual(
            final_filters[0]["computed_week_type"], ClassSession.WeekTypeChoices.EVERY
        )

        retrieve_response = self.api_client.get(f"/api/displays/screens/{screen_id}/")
        self.assertEqual(retrieve_response.status_code, 200)
        self.assertEqual(len(retrieve_response.data["data"]["screen"]["filters"]), 1)

    def test_public_view_renders_json_and_html(self):
        self._create_session()
        self._set_screen_filters(
            [
                {
                    "classroom": self.classroom.id,
                    "day_of_week": "شنبه",
                }
            ]
        )

        json_response = self.client.get(f"/displays/{self.screen.slug}/")
        self.assertEqual(json_response.status_code, 200)
        self.assertTrue(json_response.json()["success"])

        html_response = self.client.get(f"/displays/{self.screen.slug}/?format=html")
        self.assertEqual(html_response.status_code, 200)
        self.assertIn(b"<html", html_response.content.lower())
        self.assertIn(self.screen.title.encode(), html_response.content)

    def test_admin_preview_action_returns_redirect(self):
        factory = RequestFactory()
        request = factory.get("/admin/displays/displayscreen/")
        request.user = self.user
        admin_instance = DisplayScreenAdmin(DisplayScreen, AdminSite())

        queryset = DisplayScreen.objects.filter(pk=self.screen.pk)
        response = admin_instance.preview_screen(request, queryset)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertIn(self.screen.slug, response.url)

    def test_slug_lookup_returns_screen(self):
        found_screen = display_service.get_display_screen_by_slug_or_404(self.screen.slug)
        self.assertEqual(found_screen.id, self.screen.id)

    def test_html_view_handles_missing_screen(self):
        response = self.client.get("/displays/unknown/?format=html")
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"error", response.content.lower())
