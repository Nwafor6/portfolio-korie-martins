from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from core.models.user import User


class UserRegistrationTests(APITestCase):
    def test_user_registration(self):
        url = reverse("register")
        data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "phone": "1234567890",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, "test@example.com")


class ResendActivationTokenTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpassword123", is_active=False
        )

    def test_resend_activation_token(self):
        url = reverse("resend_activation_token")
        data = {"email": "test@example.com"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


from core.models.user import Otp


class VerifyTokenTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpassword123", is_active=False
        )
        self.otp = Otp.objects.create(user=self.user)

    def test_verify_token(self):
        url = reverse("verify-token")
        data = {"email": "test@example.com", "token": self.otp.token}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)


class LoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpassword123", is_active=True
        )

    def test_login(self):
        url = reverse("login")
        data = {"email": "test@example.com", "password": "testpassword123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data["data"])


class AdminLoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="admin@example.com",
            password="adminpassword123",
            is_staff=True,
            is_active=True,
        )

    def test_admin_login(self):
        url = reverse("admin-login")
        data = {"email": "admin@example.com", "password": "adminpassword123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data["data"])


class RequestPasswordResetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpassword123"
        )

    def test_request_password_reset(self):
        url = reverse("request-password-reset")
        data = {"email": "test@example.com"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SetNewPasswordTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpassword123"
        )
        self.otp = Otp.objects.create(user=self.user)

    def test_set_new_password(self):
        url = reverse("set-new-password")
        data = {
            "email": "test@example.com",
            "token": self.otp.token,
            "password": "newpassword123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword123"))


class ChangePasswordInDashboardTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpassword123"
        )
        self.client.force_authenticate(user=self.user)

    def test_change_password_in_dashboard(self):
        url = reverse("change-password")
        data = {"current_password": "testpassword123", "new_password": "newpassword123"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword123"))


class UpdateProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpassword123"
        )
        self.client.force_authenticate(user=self.user)

    def test_update_profile(self):
        url = reverse("update-profile")
        data = {"full_name": "New Name", "phone": "9876543210"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, "New Name")
        self.assertEqual(self.user.phone, "9876543210")


class GetSingleUserProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpassword123"
        )
        self.client.force_authenticate(user=self.user)

    def test_get_single_user_profile(self):
        url = reverse("get-profile", args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["email"], "test@example.com")


from core.models.user import UserActivity


class GetUserActivitiesTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpassword123"
        )
        self.client.force_authenticate(user=self.user)
        UserActivity.objects.create(
            user=self.user, activity_type="login", description="User logged in"
        )

    def test_get_user_activities(self):
        url = reverse("activities", args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)


class RecentActivitiesTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpassword123"
        )
        self.client.force_authenticate(user=self.user)
        UserActivity.objects.create(
            user=self.user, activity_type="login", description="User logged in"
        )

    def test_recent_activities(self):
        url = reverse("recent-activities")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
