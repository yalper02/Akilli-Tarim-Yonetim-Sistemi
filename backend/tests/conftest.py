import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

LOGIN_URL = "/api/v1/auth/login/"
REFRESH_URL = "/api/v1/auth/refresh/"
LOGOUT_URL = "/api/v1/auth/logout/"
ME_URL = "/api/v1/auth/me/"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def role_farmer(db):
    from apps.accounts.models import Role

    role, _ = Role.objects.get_or_create(name=Role.FARMER)
    return role


@pytest.fixture
def role_manager(db):
    from apps.accounts.models import Role

    role, _ = Role.objects.get_or_create(name=Role.FARM_MANAGER)
    return role


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="farmer1", password="StrongPass1!", first_name="Ali", last_name="Yılmaz"
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="outsider", password="StrongPass1!")


@pytest.fixture
def farm(db, user):
    from apps.farms.models import Farm

    return Farm.objects.create(name="Test Farm", owner=user)


@pytest.fixture
def membership(db, user, farm, role_farmer):
    from apps.accounts.models import FarmMembership

    return FarmMembership.objects.create(user=user, farm=farm, role=role_farmer)


@pytest.fixture
def auth_tokens(api_client, user):
    """Return access + refresh token pair for `user`."""
    res = api_client.post(LOGIN_URL, {"username": "farmer1", "password": "StrongPass1!"})
    assert res.status_code == 200
    return res.data


@pytest.fixture
def auth_client(api_client, auth_tokens):
    """APIClient pre-configured with a valid access token."""
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_tokens['access']}")
    return api_client
