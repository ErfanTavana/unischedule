from datetime import date, time, timedelta
from django.test import TestCase
from rest_framework.test import APIClient

from institutions.models import Institution
from accounts.models import User
from professors.models import Professor
from courses.models import Course
from locations.models import Building, Classroom
from semesters.models import Semester
from schedules.models import ClassSession
from schedules.services import class_session_service
from schedules.serializers.class_adjustment_serializers import (
    CreateClassCancellationSerializer,
)
from unischedule.core.exceptions import CustomValidationError
from unischedule.core.error_codes import ErrorCodes


class ClassSessionModelServiceViewTests(TestCase):
    def setUp(self):
        self.institution = Institution.objects.create(name="Uni", slug="uni")
        self.user = User.objects.create_user(username="test", password="pass", institution=self.institution)
        self.professor = Professor.objects.create(institution=self.institution, first_name="Ali", last_name="Ahmadi", national_code="1234567890")
        self.course = Course.objects.create(institution=self.institution, code="C1", title="Course1", professor=self.professor, offer_code="O1", unit_count=3)
        self.building = Building.objects.create(title="B1", institution=self.institution)
        self.classroom = Classroom.objects.create(title="101", building=self.building)
        self.semester = Semester.objects.create(institution=self.institution, title="Fall", start_date=date(2024,1,1), end_date=date(2024,6,1))
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def _session_payload(self, **overrides):
        data = {
            "course": self.course.id,
            "professor": self.professor.id,
            "classroom": self.classroom.id,
            "semester": self.semester.id,
            "day_of_week": "شنبه",
            "start_time": "08:00",
            "end_time": "10:00",
            "week_type": "every",
            "group_code": "A",
            "capacity": 30,
            "note": "",
        }
        data.update(overrides)
        return data

    def _assert_institution_required_response(self, response):
        self.assertEqual(response.status_code, ErrorCodes.INSTITUTION_REQUIRED["status_code"])
        self.assertEqual(response.data["code"], ErrorCodes.INSTITUTION_REQUIRED["code"])
        self.assertEqual(response.data["message"], ErrorCodes.INSTITUTION_REQUIRED["message"])

    def test_model_creation_and_soft_delete(self):
        session = ClassSession.objects.create(
            institution=self.institution,
            course=self.course,
            professor=self.professor,
            classroom=self.classroom,
            semester=self.semester,
            day_of_week="شنبه",
            start_time=time(8,0),
            end_time=time(10,0),
        )
        self.assertEqual(ClassSession.objects.count(), 1)
        session.delete()
        self.assertTrue(ClassSession.objects_with_deleted.filter(id=session.id, is_deleted=True).exists())

    def test_service_create_and_retrieve(self):
        # موفق: ایجاد و بازیابی جلسه بدون هیچ تداخل زمانی
        data = self._session_payload()
        created = class_session_service.create_class_session(data, self.institution)
        self.assertEqual(ClassSession.objects.count(), 1)
        retrieved = class_session_service.get_class_session_by_id_or_404(created["id"], self.institution)
        self.assertEqual(retrieved["id"], created["id"])

    def test_service_prevents_conflict(self):
        # تداخل استاد: تلاش برای ایجاد جلسهٔ جدید با همان استاد و بازهٔ زمانی متداخل
        class_session_service.create_class_session(self._session_payload(), self.institution)
        with self.assertRaises(CustomValidationError):
            class_session_service.create_class_session(self._session_payload(start_time="09:00"), self.institution)

    def test_view_create_retrieve_delete(self):
        # موفق: جریان کامل ایجاد، دریافت و حذف جلسه از طریق API
        response = self.client.post("/api/schedules/create/", self._session_payload(), format="json")
        self.assertEqual(response.status_code, 201)
        session_id = response.data["data"]["class_session"]["id"]
        res_get = self.client.get(f"/api/schedules/{session_id}/")
        self.assertEqual(res_get.status_code, 200)
        # تداخل کلاس: تلاش برای رزرو کلاس در بازهٔ زمانی متداخل برای همان کلاس
        res_conflict = self.client.post("/api/schedules/create/", self._session_payload(start_time="09:00"), format="json")
        self.assertEqual(res_conflict.status_code, 400)
        del_res = self.client.delete(f"/api/schedules/{session_id}/delete/")
        self.assertEqual(del_res.status_code, 200)
        self.assertTrue(ClassSession.objects_with_deleted.get(id=session_id).is_deleted)

    def test_views_require_institution_for_authenticated_user(self):
        # تداخل کلاس/موسسه: کاربر بدون موسسه نمی‌تواند با سرویس تعامل کند و خطای مرتبط دریافت می‌کند
        user_without_institution = User.objects.create_user(username="noinst", password="pass")
        other_client = APIClient()
        other_client.force_authenticate(user=user_without_institution)

        session = ClassSession.objects.create(
            institution=self.institution,
            course=self.course,
            professor=self.professor,
            classroom=self.classroom,
            semester=self.semester,
            day_of_week="شنبه",
            start_time=time(8, 0),
            end_time=time(10, 0),
        )

        list_response = other_client.get("/api/schedules/")
        self._assert_institution_required_response(list_response)

        retrieve_response = other_client.get(f"/api/schedules/{session.id}/")
        self._assert_institution_required_response(retrieve_response)

        create_response = other_client.post("/api/schedules/create/", self._session_payload(), format="json")
        self._assert_institution_required_response(create_response)

        update_response = other_client.put(
            f"/api/schedules/{session.id}/update/",
            {"note": "Updated"},
            format="json",
        )
        self._assert_institution_required_response(update_response)

        delete_response = other_client.delete(f"/api/schedules/{session.id}/delete/")
        self._assert_institution_required_response(delete_response)


class ClassCancellationValidationTests(TestCase):
    def setUp(self) -> None:
        self.institution = Institution.objects.create(name="Uni", slug="uni-cancel")
        self.professor = Professor.objects.create(
            institution=self.institution,
            first_name="Sara",
            last_name="Karimi",
            national_code="9876543210",
        )
        self.course = Course.objects.create(
            institution=self.institution,
            code="C2",
            title="Course 2",
            professor=self.professor,
            offer_code="O2",
            unit_count=2,
        )
        self.building = Building.objects.create(title="Main", institution=self.institution)
        self.classroom = Classroom.objects.create(title="201", building=self.building)
        self.semester = Semester.objects.create(
            institution=self.institution,
            title="Winter",
            start_date=date(2024, 1, 6),
            end_date=date(2024, 3, 30),
        )

    def _create_session(self, **overrides) -> ClassSession:
        payload = {
            "institution": self.institution,
            "course": self.course,
            "professor": self.professor,
            "classroom": self.classroom,
            "semester": self.semester,
            "day_of_week": "شنبه",
            "start_time": time(10, 0),
            "end_time": time(12, 0),
            "week_type": ClassSession.WeekTypeChoices.EVERY,
        }
        payload.update(overrides)
        return ClassSession.objects.create(**payload)

    def test_rejects_date_with_mismatched_day_of_week(self) -> None:
        session = self._create_session()
        serializer = CreateClassCancellationSerializer(
            data={"class_session": session.id, "date": date(2024, 1, 7)}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("date", serializer.errors)
        self.assertIn("روز برگزاری", serializer.errors["date"][0])

    def test_rejects_date_with_mismatched_week_type(self) -> None:
        session = self._create_session(week_type=ClassSession.WeekTypeChoices.EVEN)
        serializer = CreateClassCancellationSerializer(
            data={"class_session": session.id, "date": self.semester.start_date}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("date", serializer.errors)
        self.assertIn("نوع هفته", serializer.errors["date"][0])

    def test_accepts_matching_day_and_week_type(self) -> None:
        session = self._create_session(week_type=ClassSession.WeekTypeChoices.EVEN)
        valid_date = self.semester.start_date + timedelta(days=7)
        serializer = CreateClassCancellationSerializer(
            data={"class_session": session.id, "date": valid_date}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
