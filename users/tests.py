from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import Worker


class WorkerModelTest(TestCase):
    def test_create_worker(self):
        worker = Worker.objects.create_user(
            username="testworker",
            password="test12345",
            first_name="Ali",
            last_name="Valiyev",
            role="worker"
        )
        self.assertEqual(worker.username, "testworker")
        self.assertEqual(worker.role, "worker")
        self.assertTrue(worker.check_password("test12345"))

    def test_create_admin(self):
        admin = Worker.objects.create_superuser(
            username="testadmin",
            password="admin12345",
        )
        self.assertEqual(admin.role, "admin")
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_worker_str(self):
        worker = Worker.objects.create_user(
            username="strtest",
            password="test12345",
            first_name="Hasan",
            last_name="Karimov"
        )
        self.assertIn("strtest", str(worker))


class LoginAPITest(APITestCase):
    def setUp(self):
        self.admin = Worker.objects.create_user(
            username="admin",
            password="admin12345",
            role="admin"
        )
        self.worker = Worker.objects.create_user(
            username="worker1",
            password="worker12345",
            role="worker"
        )
        self.url = reverse("login")

    def test_login_admin_success(self):
        res = self.client.post(self.url, {
            "username": "admin",
            "password": "admin12345"
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)
        self.assertEqual(res.data["role"], "admin")

    def test_login_worker_success(self):
        res = self.client.post(self.url, {
            "username": "worker1",
            "password": "worker12345"
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["role"], "worker")

    def test_login_wrong_password(self):
        res = self.client.post(self.url, {
            "username": "admin",
            "password": "wrongpassword"
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields(self):
        res = self.client.post(self.url, {
            "username": "admin"
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class WorkerCRUDTest(APITestCase):
    def setUp(self):
        self.admin = Worker.objects.create_user(
            username="admin",
            password="admin12345",
            role="admin",
            is_staff=True
        )
        self.worker = Worker.objects.create_user(
            username="worker1",
            password="worker12345",
            role="worker"
        )
        # Admin token olish
        res = self.client.post(reverse("login"), {
            "username": "admin",
            "password": "admin12345"
        }, format="json")
        self.token = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_get_workers_list(self):
        res = self.client.get(reverse("worker-list"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res.data, list)

    def test_create_worker(self):
        res = self.client.post(reverse("worker-create"), {
            "username": "newworker",
            "password": "newpass123",
            "first_name": "Yangi",
            "last_name": "Ishchi",
            "number": "+998901234567",
            "living_address": "Tashkent",
            "work_type": "yuvuvchi",
            "percentage_work": 30,
            "work_day": "Du-Ju",
            "rest_day": "Sha-Ya",
            "role": "worker"
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["username"], "newworker")

    def test_delete_worker(self):
        res = self.client.delete(
            reverse("worker-detail", kwargs={"pk": self.worker.id})
        )
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Worker.objects.filter(id=self.worker.id).exists())

    def test_worker_cannot_access_admin_endpoints(self):
        # Worker token
        res = self.client.post(reverse("login"), {
            "username": "worker1",
            "password": "worker12345"
        }, format="json")
        worker_token = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {worker_token}")

        res = self.client.get(reverse("worker-list"))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_me_endpoint(self):
        res = self.client.get(reverse("me"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["username"], "admin")

    def test_unauthenticated_access(self):
        self.client.credentials()
        res = self.client.get(reverse("worker-list"))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)