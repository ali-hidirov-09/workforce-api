from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import Worker
from orders.models import Order, OrderType


class OrderModelTest(TestCase):
    def setUp(self):
        self.worker = Worker.objects.create_user(
            username="worker1", password="test12345", role="worker"
        )
        self.order_type = OrderType.objects.create(name="Gilam")

    def test_create_order(self):
        order = Order.objects.create(
            name="Ali Valiyev",
            number="+998901234567",
            address="Tashkent",
            date="2025-11-01",
            type=self.order_type,
            width=3.0,
            height=4.0,
            price=250000,
            status="washing",
            worker=self.worker
        )
        self.assertEqual(order.name, "Ali Valiyev")
        self.assertEqual(order.status, "washing")
        self.assertEqual(str(order.type), "Gilam")

    def test_order_default_status(self):
        order = Order.objects.create(
            name="Test",
            number="123",
            address="Test",
            date="2025-11-01",
            price=0
        )
        self.assertEqual(order.status, "washing")


class AdminOrderAPITest(APITestCase):
    def setUp(self):
        self.admin = Worker.objects.create_user(
            username="admin", password="admin12345", role="admin"
        )
        self.worker = Worker.objects.create_user(
            username="worker1", password="worker12345", role="worker"
        )
        self.order_type = OrderType.objects.create(name="Gilam")
        self.order = Order.objects.create(
            name="Test Mijoz",
            number="+998901234567",
            address="Tashkent",
            date="2025-11-01",
            type=self.order_type,
            price=250000,
            status="washing",
            worker=self.worker
        )

        # Admin token
        res = self.client.post(reverse("login"), {
            "username": "admin", "password": "admin12345"
        }, format="json")
        self.token = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_get_all_orders(self):
        res = self.client.get(reverse("admin-order-list"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_get_orders_filter_by_status(self):
        res = self.client.get(reverse("admin-order-list") + "?status=washing")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_get_orders_filter_no_result(self):
        res = self.client.get(reverse("admin-order-list") + "?status=delivered")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 0)

    def test_get_order_detail(self):
        res = self.client.get(
            reverse("admin-order-detail", kwargs={"pk": self.order.id})
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], "Test Mijoz")

    def test_update_order_status(self):
        res = self.client.patch(
            reverse("admin-order-detail", kwargs={"pk": self.order.id}),
            {"status": "bringing"},
            format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "bringing")

    def test_delete_order(self):
        res = self.client.delete(
            reverse("admin-order-detail", kwargs={"pk": self.order.id})
        )
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())

    def test_dashboard_stats(self):
        res = self.client.get(reverse("dashboard-stats"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("total_orders", res.data)
        self.assertIn("total_revenue", res.data)
        self.assertEqual(res.data["total_orders"], 1)


class WorkerOrderAPITest(APITestCase):
    def setUp(self):
        self.worker = Worker.objects.create_user(
            username="worker1", password="worker12345", role="worker"
        )
        self.order_type = OrderType.objects.create(name="Gilam")

        # Worker token
        res = self.client.post(reverse("login"), {
            "username": "worker1", "password": "worker12345"
        }, format="json")
        self.token = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_worker_add_order(self):
        res = self.client.post(reverse("worker-order-create"), {
            "name": "Mijoz Ism",
            "number": "+998901112233",
            "address": "Andijon",
            "date": "2025-11-01",
            "type_name": "Gilam",
            "width": 3.0,
            "height": 4.0,
            "price": 250000,
            "status": "washing"
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_worker_sees_only_own_orders(self):
        # Boshqa worker
        other_worker = Worker.objects.create_user(
            username="worker2", password="worker12345", role="worker"
        )
        Order.objects.create(
            name="Boshqa", number="123", address="Test",
            date="2025-11-01", price=0, worker=other_worker
        )
        Order.objects.create(
            name="O'zniki", number="456", address="Test",
            date="2025-11-01", price=0, worker=self.worker
        )
        res = self.client.get(reverse("worker-order-list"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], "O'zniki")

    def test_worker_cannot_access_admin_orders(self):
        res = self.client.get(reverse("admin-order-list"))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)