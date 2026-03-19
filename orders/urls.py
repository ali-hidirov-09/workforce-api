from django.urls import path
from .views import (
    AdminOrderListView, AdminOrderDetailView, DashboardStatsView,
    WorkerOrderCreateView, WorkerOrderListView, WorkerOrderUpdateView,
    OrderTypeListView,
)

urlpatterns = [
    # Admin
    path('admin-dashboard/orders', AdminOrderListView.as_view(), name='admin-order-list'),
    path('admin-dashboard/orders/<int:pk>/', AdminOrderDetailView.as_view(), name='admin-order-detail'),
    path('admin-dashboard/stats', DashboardStatsView.as_view(), name='dashboard-stats'),

    # Worker
    path('worker/orders/', WorkerOrderListView.as_view(), name='worker-order-list'),
    path('worker/orders/add/', WorkerOrderCreateView.as_view(), name='worker-order-create'),
    path('worker/orders/<int:pk>/status/', WorkerOrderUpdateView.as_view(), name='worker-order-update'),

    # Umumiy
    path('order-types/', OrderTypeListView.as_view(), name='order-types'),
]
