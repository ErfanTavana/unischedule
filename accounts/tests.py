from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase

from unischedule.core.error_codes import ErrorCodes
from unischedule.core.success_codes import SuccessCodes


class ChangePasswordAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="OldPassword123",
        )
        self.url = "/api/auth/change-password/"
        self.client.force_authenticate(user=self.user)

    def test_change_password_success(self):
        payload = {
            "old_password": "OldPassword123",
            "new_password": "NewPassword123!",
            "confirm_new_password": "NewPassword123!",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["code"], SuccessCodes.PASSWORD_CHANGE_SUCCESS["code"])
        self.assertEqual(response.data["message"], SuccessCodes.PASSWORD_CHANGE_SUCCESS["message"])

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(payload["new_password"]))

    def test_change_password_incorrect_current_password(self):
        payload = {
            "old_password": "WrongPassword",
            "new_password": "AnotherPassword123",
            "confirm_new_password": "AnotherPassword123",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, ErrorCodes.PASSWORD_INCORRECT["status_code"])
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["code"], ErrorCodes.PASSWORD_INCORRECT["code"])
        self.assertEqual(response.data["message"], ErrorCodes.PASSWORD_INCORRECT["message"])

    def test_change_password_mismatch(self):
        payload = {
            "old_password": "OldPassword123",
            "new_password": "NewPassword123",
            "confirm_new_password": "MismatchPassword123",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, ErrorCodes.VALIDATION_FAILED["status_code"])
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["code"], ErrorCodes.VALIDATION_FAILED["code"])
        self.assertIn("confirm_new_password", response.data["errors"])

    def test_change_password_same_as_old(self):
        payload = {
            "old_password": "OldPassword123",
            "new_password": "OldPassword123",
            "confirm_new_password": "OldPassword123",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, ErrorCodes.VALIDATION_FAILED["status_code"])
        self.assertFalse(response.data["success"])
        self.assertIn("new_password", response.data["errors"])

    def test_change_password_does_not_meet_policy(self):
        payload = {
            "old_password": "OldPassword123",
            "new_password": "short",
            "confirm_new_password": "short",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, ErrorCodes.VALIDATION_FAILED["status_code"])
        self.assertFalse(response.data["success"])
        self.assertIn("new_password", response.data["errors"])
        self.assertTrue(
            any(
                "short" in message.lower() or "at least" in message.lower()
                for message in response.data["errors"]["new_password"]
            )
        )
