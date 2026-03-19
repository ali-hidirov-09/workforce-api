from rest_framework import serializers
from .models import Order, OrderType


class OrderTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderType
        fields = ['id', 'name']


class OrderSerializer(serializers.ModelSerializer):
    type = OrderTypeSerializer(read_only=True)
    type_id = serializers.PrimaryKeyRelatedField(
        queryset=OrderType.objects.all(),
        source='type',
        write_only=True,
        required=False,
        allow_null=True
    )
    # Worker frontenddagi kabi "type": {"name": "..."} ni kutadi
    worker_name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'name', 'number', 'address', 'date', 'izox',
            'type', 'type_id', 'width', 'height', 'kg',
            'price', 'status', 'worker', 'worker_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['worker', 'created_at', 'updated_at']

    def get_worker_name(self, obj):
        if obj.worker:
            return f"{obj.worker.first_name} {obj.worker.last_name}"
        return None


class OrderCreateSerializer(serializers.ModelSerializer):
    """Worker zakaz qo'shish uchun — type nomi bilan"""
    type_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Order
        fields = [
            'name', 'number', 'address', 'date', 'izox',
            'type_name', 'width', 'height', 'kg', 'price', 'status'
        ]

    def create(self, validated_data):
        type_name = validated_data.pop('type_name', None)
        order_type = None
        if type_name:
            order_type, _ = OrderType.objects.get_or_create(name=type_name)

        request = self.context.get('request')
        worker = request.user if request else None

        order = Order.objects.create(
            type=order_type,
            worker=worker,
            **validated_data
        )
        return order
