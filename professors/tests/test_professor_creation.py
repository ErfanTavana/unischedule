from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from institutions.models import Institution
from accounts.models import User


class ProfessorCreationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.institution = Institution.objects.create(name="Test Institution", slug="test-institution")
        self.user = User.objects.create_user(
            username="testuser", password="password", institution=self.institution
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("create-professor")
        self.professor_data = {
            "first_name": "Ali",
            "last_name": "Reza",
            "national_code": "1234567890",
            "phone_number": "09123456789",
        }

    def test_duplicate_national_code_returns_400(self):
        first_response = self.client.post(self.url, self.professor_data, format="json")
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)

        # Attempting to create the same professor again verifies the API's
        # protection against duplicate national codes.
        second_response = self.client.post(self.url, self.professor_data, format="json")
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
