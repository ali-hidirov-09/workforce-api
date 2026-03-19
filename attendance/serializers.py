from rest_framework import serializers
from .models import Attendance
from users.serializers import WorkerSerializer


class AttendanceSerializer(serializers.ModelSerializer):
    worker_name = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = ['id', 'worker', 'worker_name', 'date', 'status']

    def get_worker_name(self, obj):
        return f"{obj.worker.first_name} {obj.worker.last_name}"


class AttendanceBulkSerializer(serializers.Serializer):
    """
    Bir haftalik davomat birdan yuborish uchun.
    Format: [{"worker": 1, "date": "2025-01-01", "status": "present"}, ...]
    """
    records = AttendanceSerializer(many=True)

    def create(self, validated_data):
        results = []
        for record in validated_data['records']:
            obj, _ = Attendance.objects.update_or_create(
                worker=record['worker'],
                date=record['date'],
                defaults={'status': record['status']}
            )
            results.append(obj)
        return results
