from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import Worker
from attendance.models import Attendance
from datetime import date


class AttendanceModelTest(TestCase):
    def setUp(self):
        self.worker = Worker.objects.create_user(
            username="worker1", password="test12345", role="worker"
        )

    def test_create_attendance(self):
        att = Attendance.objects.create(
            worker=self.worker,
            date=date(2025, 11, 1),
            status="present"
        )
        self.assertEqual(att.status, "present")
        self.assertEqual(att.worker.username, "worker1")

    def test_unique_together(self):
        Attendance.objects.create(
            worker=self.worker,
            date=date(2025, 11, 1),
            status="present"
        )
        # Xuddi shu kun yana qo'shish mumkin emas
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Attendance.objects.create(
                worker=self.worker,
                date=date(2025, 11, 1),
                status="absent"
            )


class AttendanceAPITest(APITestCase):
    def setUp(self):
        self.admin = Worker.objects.create_user(
            username="admin", password="admin12345", role="admin"
        )
        self.worker = Worker.objects.create_user(
            username="worker1", password="worker12345", role="worker",
            first_name="Ali", last_name="Valiyev"
        )
        # Admin token
        res = self.client.post(reverse("login"), {
            "username": "admin", "password": "admin12345"
        }, format="json")
        self.token = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_mark_attendance_present(self):
        res = self.client.post(reverse("attendance-mark"), {
            "worker": self.worker.id,
            "date": "2025-11-03",
            "status": "present"
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["status"], "present")

    def test_mark_attendance_absent(self):
        res = self.client.post(reverse("attendance-mark"), {
            "worker": self.worker.id,
            "date": "2025-11-04",
            "status": "absent"
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["status"], "absent")

    def test_update_attendance(self):
        # Avval present qilamiz
        self.client.post(reverse("attendance-mark"), {
            "worker": self.worker.id,
            "date": "2025-11-03",
            "status": "present"
        }, format="json")
        # Keyin absent ga o'zgartiramiz
        res = self.client.post(reverse("attendance-mark"), {
            "worker": self.worker.id,
            "date": "2025-11-03",
            "status": "absent"
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["status"], "absent")
        # DB da faqat 1 ta yozuv bo'lishi kerak
        self.assertEqual(
            Attendance.objects.filter(worker=self.worker, date="2025-11-03").count(), 1
        )

    def test_bulk_attendance(self):
        worker2 = Worker.objects.create_user(
            username="worker2", password="test12345", role="worker"
        )
        res = self.client.post(reverse("attendance-bulk"), {
            "records": [
                {"worker": self.worker.id, "date": "2025-11-03", "status": "present"},
                {"worker": worker2.id,      "date": "2025-11-03", "status": "absent"},
                {"worker": self.worker.id,  "date": "2025-11-04", "status": "present"},
            ]
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 3)

    def test_get_attendance_list(self):
        Attendance.objects.create(
            worker=self.worker, date="2025-11-03", status="present"
        )
        res = self.client.get(reverse("attendance-list"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_get_attendance_by_week(self):
        Attendance.objects.create(worker=self.worker, date="2025-11-03", status="present")
        Attendance.objects.create(worker=self.worker, date="2025-12-15", status="absent")
        res = self.client.get(reverse("attendance-list") + "?week_start=2025-11-03")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_invalid_status(self):
        res = self.client.post(reverse("attendance-mark"), {
            "worker": self.worker.id,
            "date": "2025-11-03",
            "status": "noto'g'ri_status"
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_worker_cannot_access_attendance(self):
        res = self.client.post(reverse("login"), {
            "username": "worker1", "password": "worker12345"
        }, format="json")
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {res.data['access']}"
        )
        res = self.client.get(reverse("attendance-list"))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_missing_fields(self):
        res = self.client.post(reverse("attendance-mark"), {
            "worker": self.worker.id,
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)