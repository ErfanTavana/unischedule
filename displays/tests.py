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
        self.second_building = Building.objects.create(title="Annex", institution=self.institution)
        self.second_classroom = Classroom.objects.create(title="102", building=self.second_building)
        self.other_building = Building.objects.create(title="Remote", institution=self.other_institution)

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
            group_code="A",
            capacity=20,
        )
        data.update(overrides)
        return ClassSession.objects.create(**data)

    def _update_screen_filter(self, **data):
        display_service.update_display_screen(self.screen, data)
        self.screen.refresh_from_db()

    def test_service_generates_payload_with_classroom_filter(self):
        self._create_session()
        self._create_session(
            classroom=self.second_classroom,
            group_code="B",
            start_time=time(12, 0),
            end_time=time(14, 0),
            capacity=10,
        )
        self._update_screen_filter(
            filter_classroom=self.classroom.id,
            filter_building=self.building.id,
            filter_day_of_week="شنبه",
            filter_capacity=15,
            filter_is_active=True,
        )

        payload = display_service.build_public_payload(self.screen, use_cache=False)

        self.assertIn("sessions", payload)
        self.assertEqual(len(payload["sessions"]), 1)
        self.assertEqual(payload["sessions"][0]["classroom_title"], self.classroom.title)
        self.assertEqual(payload["filter"]["computed_day_of_week"], "شنبه")
        self.assertEqual(payload["filter"]["building"]["id"], self.building.id)
        self.assertEqual(payload["filter"]["capacity"], 15)

    def test_service_filters_by_professor_and_week_type(self):
        odd_session = self._create_session(week_type=ClassSession.WeekTypeChoices.ODD)
        every_session = self._create_session(week_type=ClassSession.WeekTypeChoices.EVERY, start_time=time(10, 0))
        self._create_session(week_type=ClassSession.WeekTypeChoices.EVEN, start_time=time(12, 0))

        self._update_screen_filter(
            filter_professor=self.professor.id,
            filter_week_type=ClassSession.WeekTypeChoices.ODD,
        )

        sessions = display_service.build_public_payload(self.screen, use_cache=False)["sessions"]
        session_ids = {session["id"] for session in sessions}
        self.assertIn(odd_session.id, session_ids)
        self.assertIn(every_session.id, session_ids)
        self.assertEqual(len(session_ids), 2)

    def test_service_filters_by_building_group_and_time_range(self):
        included_session = self._create_session(group_code="Z", capacity=40)
        self._create_session(
            classroom=self.second_classroom,
            group_code="Z",
            start_time=time(9, 0),
            end_time=time(11, 0),
            capacity=50,
        )
        self._create_session(group_code="Z", capacity=35, start_time=time(7, 0), end_time=time(9, 0))

        self._update_screen_filter(
            filter_building=self.building.id,
            filter_group_code="Z",
            filter_start_time=time(8, 0),
            filter_end_time=time(10, 0),
            filter_capacity=30,
        )

        payload = display_service.build_public_payload(self.screen, use_cache=False)
        self.assertEqual(len(payload["sessions"]), 1)
        self.assertEqual(payload["sessions"][0]["id"], included_session.id)
        self.assertEqual(payload["filter"]["group_code"], "Z")
        self.assertEqual(payload["filter"]["start_time"], "08:00:00")
        self.assertEqual(payload["filter"]["end_time"], "10:00:00")

    def test_filter_validation_rejects_foreign_institution(self):
        with self.assertRaises(CustomValidationError):
            display_service.update_display_screen(
                self.screen,
                {
                    "filter_professor": self.other_professor.id,
                },
            )

    def test_filter_validation_rejects_foreign_building(self):
        with self.assertRaises(CustomValidationError):
            display_service.update_display_screen(
                self.screen,
                {
                    "filter_building": self.other_building.id,
                },
            )

    def test_filter_validation_rejects_mismatched_building_and_classroom(self):
        with self.assertRaises(CustomValidationError):
            display_service.update_display_screen(
                self.screen,
                {
                    "filter_classroom": self.classroom.id,
                    "filter_building": self.second_building.id,
                },
            )

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
                "filter_title": "Classroom filter",
                "filter_classroom": self.classroom.id,
                "filter_building": self.building.id,
                "filter_semester": self.semester.id,
                "filter_day_of_week": "شنبه",
            },
            format="json",
        )
        self.assertEqual(screen_response.status_code, 201)
        screen_data = screen_response.data["data"]["screen"]
        screen_id = screen_data["id"]
        self.assertEqual(screen_data["filter_classroom"], self.classroom.id)
        self.assertEqual(screen_data["filter_building"], self.building.id)
        self.assertEqual(screen_data["filter_semester"], self.semester.id)
        self.assertEqual(screen_data["filter_day_of_week"], "شنبه")
        self.assertTrue(screen_data["filter_is_active"])

        update_response = self.api_client.put(
            f"/api/displays/screens/{screen_id}/update/",
            {
                "filter_title": "Professor filter",
                "filter_professor": self.professor.id,
                "filter_week_type": ClassSession.WeekTypeChoices.ODD,
                "filter_classroom": None,
                "filter_building": None,
                "filter_semester": None,
            },
            format="json",
        )
        self.assertEqual(update_response.status_code, 200)
        updated_screen = update_response.data["data"]["screen"]
        self.assertEqual(updated_screen["filter_professor"], self.professor.id)
        self.assertIsNone(updated_screen["filter_classroom"])
        self.assertEqual(
            updated_screen["filter_computed_week_type"], ClassSession.WeekTypeChoices.ODD
        )

        disable_response = self.api_client.put(
            f"/api/displays/screens/{screen_id}/update/",
            {
                "filter_is_active": False,
            },
            format="json",
        )
        self.assertEqual(disable_response.status_code, 200)
        disabled_screen = disable_response.data["data"]["screen"]
        self.assertFalse(disabled_screen["filter_is_active"])

        retrieve_response = self.api_client.get(f"/api/displays/screens/{screen_id}/")
        self.assertEqual(retrieve_response.status_code, 200)
        retrieved_screen = retrieve_response.data["data"]["screen"]
        self.assertFalse(retrieved_screen["filter_is_active"])

    def test_public_view_returns_json_payload(self):
        self._create_session()
        self._update_screen_filter(
            filter_classroom=self.classroom.id,
            filter_day_of_week="شنبه",
        )

        json_response = self.client.get(f"/displays/{self.screen.slug}/")
        self.assertEqual(json_response.status_code, 200)
        self.assertTrue(json_response.json()["success"])
        self.assertEqual(json_response["Content-Type"], "application/json")

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

    def test_public_view_missing_screen_returns_json_error(self):
        response = self.client.get("/displays/unknown/")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(response["Content-Type"], "application/json")
