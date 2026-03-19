from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order, OrderType
from .serializers import OrderSerializer, OrderCreateSerializer, OrderTypeSerializer
from django.db.models import Sum, Count
from django.utils import timezone


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsWorker(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'worker'


# ─── Admin: barcha zakazlar ─────────────────────────────
class AdminOrderListView(generics.ListAPIView):
    queryset = Order.objects.select_related('type', 'worker').all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs


# ─── Admin: zakaz detail (ko'rish, tahrirlash, o'chirish) ─
class AdminOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.select_related('type', 'worker').all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdmin]


# ─── Admin: dashboard statistika ────────────────────────
class DashboardStatsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        today = timezone.now().date()
        month_start = today.replace(day=1)

        total_orders    = Order.objects.count()
        today_orders    = Order.objects.filter(created_at__date=today).count()
        month_orders    = Order.objects.filter(created_at__date__gte=month_start).count()
        total_revenue   = Order.objects.aggregate(Sum('price'))['price__sum'] or 0
        month_revenue   = Order.objects.filter(
            created_at__date__gte=month_start
        ).aggregate(Sum('price'))['price__sum'] or 0

        by_status = Order.objects.values('status').annotate(count=Count('id'))

        return Response({
            'total_orders': total_orders,
            'today_orders': today_orders,
            'month_orders': month_orders,
            'total_revenue': total_revenue,
            'month_revenue': month_revenue,
            'by_status': list(by_status),
        })


# ─── Worker: zakaz qo'shish ─────────────────────────────
class WorkerOrderCreateView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [IsWorker]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


# ─── Worker: o'z zakazlarini ko'rish ────────────────────
class WorkerOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsWorker]

    def get_queryset(self):
        return Order.objects.filter(worker=self.request.user).select_related('type')


# ─── Worker: o'z zakazining statusini o'zgartirish ──────
class WorkerOrderUpdateView(generics.UpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsWorker]

    def get_queryset(self):
        return Order.objects.filter(worker=self.request.user)

    def patch(self, request, *args, **kwargs):
        # Worker faqat statusni o'zgartira oladi
        order = self.get_object()
        new_status = request.data.get('status')
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({'detail': 'Noto\'g\'ri status'}, status=400)
        order.status = new_status
        order.save()
        return Response(OrderSerializer(order).data)


# ─── Order turlari ──────────────────────────────────────
class OrderTypeListView(generics.ListCreateAPIView):
    queryset = OrderType.objects.all()
    serializer_class = OrderTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
