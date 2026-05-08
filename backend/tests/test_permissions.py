"""
IsFarmMember ve IsFarmManager yetki sınıfı testleri.
CLAUDE.md §11.1 kritik yol.
"""

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.views import APIView

from apps.accounts.permissions import IsFarmManager, IsFarmMember

# ---------------------------------------------------------------------------
# Yardımcı: farm_id kwarg barındıran sahte view
# ---------------------------------------------------------------------------


def make_view(farm_id=None):
    """Permission sınıfı için gerekli kwargs'ı simüle eden sahte view nesnesi."""

    class FakeView(APIView):
        kwargs = {}

    view = FakeView()
    if farm_id is not None:
        view.kwargs["farm_id"] = farm_id
    return view


# ---------------------------------------------------------------------------
# IsFarmMember — has_permission (URL kwarg tabanlı)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_member_has_permission(user, farm, membership):
    factory = APIRequestFactory()
    request = factory.get("/")
    force_authenticate(request, user=user)
    request.user = user

    perm = IsFarmMember()
    assert perm.has_permission(request, make_view(farm_id=farm.pk)) is True


@pytest.mark.django_db
def test_non_member_denied_at_view_level(user, other_user, farm, membership):
    factory = APIRequestFactory()
    request = factory.get("/")
    force_authenticate(request, user=other_user)
    request.user = other_user

    perm = IsFarmMember()
    # other_user üye değil — erişim reddedilmeli
    assert perm.has_permission(request, make_view(farm_id=farm.pk)) is False


@pytest.mark.django_db
def test_unauthenticated_denied(farm):
    from django.contrib.auth.models import AnonymousUser

    factory = APIRequestFactory()
    request = factory.get("/")
    request.user = AnonymousUser()

    perm = IsFarmMember()
    assert perm.has_permission(request, make_view(farm_id=farm.pk)) is False


@pytest.mark.django_db
def test_no_farm_id_kwarg_passes_to_object_level(user, farm, membership):
    """farm_id yoksa has_permission True döner; kontrol has_object_permission'a ertelenir."""
    factory = APIRequestFactory()
    request = factory.get("/")
    force_authenticate(request, user=user)
    request.user = user

    perm = IsFarmMember()
    # farm_id kwarg'sız view — izin verilmeli (object-level'a erteleme)
    assert perm.has_permission(request, make_view(farm_id=None)) is True


# ---------------------------------------------------------------------------
# IsFarmMember — has_object_permission
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_member_has_object_permission_via_farm_attr(user, farm, membership):
    """obj.farm üzerinden üyelik kontrolü."""
    from apps.devices.models import Device

    device = Device.objects.create(
        name="Sensor-01",
        device_uid="uid-001",
        device_type=Device.SENSOR,
        farm=farm,
    )

    factory = APIRequestFactory()
    request = factory.get("/")
    force_authenticate(request, user=user)
    request.user = user

    perm = IsFarmMember()
    assert perm.has_object_permission(request, make_view(), device) is True


@pytest.mark.django_db
def test_non_member_denied_at_object_level(other_user, farm, membership):
    """Üye olmayan kullanıcı nesne düzeyinde reddedilmeli."""
    factory = APIRequestFactory()
    request = factory.get("/")
    force_authenticate(request, user=other_user)
    request.user = other_user

    perm = IsFarmMember()
    # obj direkt farm nesnesi
    assert perm.has_object_permission(request, make_view(), farm) is False


@pytest.mark.django_db
def test_obj_is_farm_itself(user, farm, membership):
    """obj doğrudan Farm örneği olduğunda da çalışmalı."""
    factory = APIRequestFactory()
    request = factory.get("/")
    force_authenticate(request, user=user)
    request.user = user

    perm = IsFarmMember()
    assert perm.has_object_permission(request, make_view(), farm) is True


# ---------------------------------------------------------------------------
# IsFarmManager — rol tabanlı yazma kontrolü
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_farmer_can_read_but_not_write(user, farm, membership):
    """Farmer rolü GET yapabilir, POST/PUT/DELETE yapamaz."""
    factory = APIRequestFactory()
    perm = IsFarmManager()

    get_req = factory.get("/")
    force_authenticate(get_req, user=user)
    get_req.user = user
    assert perm.has_permission(get_req, make_view(farm_id=farm.pk)) is True

    post_req = factory.post("/")
    force_authenticate(post_req, user=user)
    post_req.user = user
    # farmer rolüyle — yazma reddedilmeli
    assert perm.has_permission(post_req, make_view(farm_id=farm.pk)) is False


@pytest.mark.django_db
def test_farm_manager_can_write(other_user, farm, role_manager):
    """farm_manager rolüne sahip kullanıcı yazabilmeli."""
    from apps.accounts.models import FarmMembership

    FarmMembership.objects.create(user=other_user, farm=farm, role=role_manager)

    factory = APIRequestFactory()
    post_req = factory.post("/")
    force_authenticate(post_req, user=other_user)
    post_req.user = other_user

    perm = IsFarmManager()
    assert perm.has_permission(post_req, make_view(farm_id=farm.pk)) is True
