import shutil
import tempfile
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from institutions.models import Institution
from unischedule.core.error_codes import ErrorCodes
from unischedule.core.success_codes import SuccessCodes


class ChangePasswordAPITestCase(TestCase):
    """End-to-end tests for the change-password API endpoint."""

    def setUp(self):
        # Create and authenticate a baseline user for each test scenario.
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="OldPassword123",
        )
        self.url = "/api/auth/change-password/"
        self.client.force_authenticate(user=self.user)

    def test_change_password_success(self):
        """Passwords should update when the payload is valid."""
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
        """Reject requests when the provided current password is incorrect."""
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
        """Ensure validation catches mismatched new password confirmation."""
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
        """Block requests that attempt to reuse the existing password."""
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
        """Validate that Django's password policy errors bubble up to the response."""
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


class InstitutionLogoAPITestCase(TestCase):
    """Integration tests for the institution logo management endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.tempdir = tempfile.mkdtemp(prefix="logo-tests-")
        self.addCleanup(shutil.rmtree, self.tempdir, ignore_errors=True)
        override = override_settings(MEDIA_ROOT=self.tempdir)
        override.enable()
        self.addCleanup(override.disable)

        self.institution = Institution.objects.create(name="Test Inst", slug="test-inst")
        self.user = get_user_model().objects.create_user(
            username="logo-user",
            password="Password123!",
            institution=self.institution,
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/auth/institution/logo/"

    def _fake_logo(self, name: str = "logo.png") -> SimpleUploadedFile:
        return SimpleUploadedFile(
            name,
            b"fake image bytes",
            content_type="image/png",
        )

    def test_get_logo_returns_empty_payload_when_missing(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["code"], SuccessCodes.INSTITUTION_LOGO_RETRIEVED["code"])
        self.assertIsNone(response.data["data"]["institution"]["logo_url"])

    def test_put_logo_updates_file(self):
        response = self.client.put(
            self.url,
            data={"logo": self._fake_logo()},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["code"], SuccessCodes.INSTITUTION_LOGO_UPDATED["code"])
        logo_url = response.data["data"]["institution"]["logo_url"]
        self.assertIsNotNone(logo_url)

    def test_delete_logo_removes_file(self):
        self.client.put(
            self.url,
            data={"logo": self._fake_logo("delete.png")},
            format="multipart",
        )

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["code"], SuccessCodes.INSTITUTION_LOGO_DELETED["code"])
        self.assertIsNone(response.data["data"]["institution"]["logo_url"])


class LoginAPITestCase(TestCase):
    """Authentication endpoint tests covering login edge cases."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="login-user",
            password="StrongPassword123!",
        )
        self.url = "/api/auth/login/"

    def test_login_handles_token_race_condition(self):
        """Simulate a concurrent token creation to ensure login still succeeds."""

        payload = {"username": "login-user", "password": "StrongPassword123!"}
        original_create = Token.objects.create

        def fake_create(*args, **kwargs):
            original_create(*args, **kwargs)
            raise IntegrityError("duplicate key value violates unique constraint")

        with patch("accounts.repositories.auth_repository.Token.objects.create", side_effect=fake_create):
            response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["code"], SuccessCodes.LOGIN_SUCCESS["code"])
        self.assertIn("token", response.data["data"])
        self.assertEqual(Token.objects.filter(user=self.user).count(), 1)
