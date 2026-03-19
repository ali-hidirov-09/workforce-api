from django.urls import path
from .views import AttendanceListView, AttendanceUpsertView, AttendanceBulkView

urlpatterns = [
    path('admin-dashboard/attendance/', AttendanceListView.as_view(), name='attendance-list'),
    path('admin-dashboard/attendance/mark/', AttendanceUpsertView.as_view(), name='attendance-mark'),
    path('admin-dashboard/attendance/bulk/', AttendanceBulkView.as_view(), name='attendance-bulk'),
]
