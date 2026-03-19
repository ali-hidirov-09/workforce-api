from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginView, MeView, WorkerListView, WorkerCreateView, WorkerDetailView

urlpatterns = [
    # Auth
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # Profilim
    path('me/', MeView.as_view(), name='me'),

    # Admin: Ishchilar
    path('admin-dashboard/users', WorkerListView.as_view(), name='worker-list'),
    path('admin-dashboard/create-user', WorkerCreateView.as_view(), name='worker-create'),
    path('admin-dashboard/users/<int:pk>/', WorkerDetailView.as_view(), name='worker-detail'),
]
