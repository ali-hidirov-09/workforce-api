from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Attendance
from .serializers import AttendanceSerializer
from datetime import date, timedelta


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class AttendanceListView(generics.ListAPIView):
    """Haftalik davomat ro'yxati. ?week_start=2025-01-06 bilan filtr"""
    serializer_class = AttendanceSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        week_start = self.request.query_params.get('week_start')
        if week_start:
            try:
                start = date.fromisoformat(week_start)
                end = start + timedelta(days=6)
                return Attendance.objects.filter(
                    date__range=(start, end)
                ).select_related('worker')
            except ValueError:
                pass
        return Attendance.objects.select_related('worker').all()


class AttendanceUpsertView(APIView):
    """
    Davomat belgilash (qo'shish yoki yangilash).
    POST: {"worker": 1, "date": "2025-01-06", "status": "present"}
    """
    permission_classes = [IsAdmin]

    def post(self, request):
        worker_id = request.data.get('worker')
        att_date  = request.data.get('date')
        att_status = request.data.get('status')

        if not all([worker_id, att_date, att_status]):
            return Response({'detail': 'worker, date, status majburiy'}, status=400)

        if att_status not in ('present', 'absent'):
            return Response({'detail': 'status: present yoki absent bo\'lishi kerak'}, status=400)

        obj, created = Attendance.objects.update_or_create(
            worker_id=worker_id,
            date=att_date,
            defaults={'status': att_status}
        )
        return Response(AttendanceSerializer(obj).data, status=201 if created else 200)


class AttendanceBulkView(APIView):
    """
    Bir nechta davomat birdan saqlash.
    POST: {"records": [{"worker": 1, "date": "...", "status": "present"}, ...]}
    """
    permission_classes = [IsAdmin]

    def post(self, request):
        records = request.data.get('records', [])
        if not records:
            return Response({'detail': 'records bo\'sh'}, status=400)

        saved = []
        for record in records:
            obj, _ = Attendance.objects.update_or_create(
                worker_id=record.get('worker'),
                date=record.get('date'),
                defaults={'status': record.get('status', 'present')}
            )
            saved.append(AttendanceSerializer(obj).data)

        return Response(saved, status=200)
