from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import User
from .serializers import UserSerializer, UserUpdateSerializer


@method_decorator(ratelimit(key="ip", rate="5/15m", method="POST", block=True), name="dispatch")
class LoginView(TokenObtainPairView):
    """POST /auth/login/ — IP başına 15 dakikada 5 deneme limiti ile token döndürür."""


class RefreshView(TokenRefreshView):
    """POST /auth/refresh/ — returns new access token (rotates refresh)."""


class LogoutView(APIView):
    """POST /auth/logout/ — blacklists the provided refresh token."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "refresh token required", "code": "missing_token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            raise AuthenticationFailed("Invalid or already blacklisted token.")
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    """GET /auth/me/ — returns current user profile + farm memberships."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User.objects.prefetch_related("memberships__role", "memberships__farm").get(
            pk=request.user.pk
        )
        return Response(UserSerializer(user).data)

    def patch(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = User.objects.prefetch_related("memberships__role", "memberships__farm").get(
            pk=request.user.pk
        )
        return Response(UserSerializer(user).data)
