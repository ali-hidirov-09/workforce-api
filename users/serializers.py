from rest_framework import serializers
from .models import Worker


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'number', 'living_address', 'work_type',
            'percentage_work', 'work_day', 'rest_day', 'role'
        ]


class WorkerCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Worker
        fields = [
            'id', 'username', 'password', 'first_name', 'last_name',
            'number', 'living_address', 'work_type',
            'percentage_work', 'work_day', 'rest_day', 'role'
        ]

    def validate_username(self, value):
        # Edit qilayotganda o'zining username ini tekshirmasin
        instance = self.instance
        if Worker.objects.filter(username=value).exclude(
            pk=instance.pk if instance else None
        ).exists():
            raise serializers.ValidationError("Bu username allaqachon mavjud.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', 'changeme123')
        worker = Worker(**validated_data)
        worker.set_password(password)
        worker.save()
        return worker

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'number', 'living_address', 'work_type', 'role'
        ]
        read_only_fields = ['username', 'role']