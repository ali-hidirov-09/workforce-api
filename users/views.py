from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Worker
from .serializers import WorkerSerializer, WorkerCreateSerializer, MeSerializer


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


@extend_schema(
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string', 'example': 'admin'},
                'password': {'type': 'string', 'example': '123456'},
            },
            'required': ['username', 'password'],
        }
    },
    responses={
        200: {
            'type': 'object',
            'properties': {
                'access':     {'type': 'string'},
                'refresh':    {'type': 'string'},
                'role':       {'type': 'string'},
                'username':   {'type': 'string'},
                'first_name': {'type': 'string'},
                'last_name':  {'type': 'string'},
            }
        }
    }
)
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {'detail': "Username yoki parol noto'g'ri"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'access':     str(refresh.access_token),
            'refresh':    str(refresh),
            'role':       user.role,
            'username':   user.username,
            'first_name': user.first_name,
            'last_name':  user.last_name,
        })


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = MeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class WorkerListView(generics.ListAPIView):
    queryset = Worker.objects.filter(role='worker')
    serializer_class = WorkerSerializer
    permission_classes = [IsAdmin]


class WorkerCreateView(generics.CreateAPIView):
    serializer_class = WorkerCreateSerializer
    permission_classes = [IsAdmin]


class WorkerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Worker.objects.filter(role='worker')
    serializer_class = WorkerCreateSerializer
    permission_classes = [IsAdmin]