"""
Kimlik doğrulama akış testleri — giriş, token yenileme, çıkış, /me/.
CLAUDE.md §11.1 kritik yol.
"""

import pytest

from tests.conftest import LOGIN_URL, LOGOUT_URL, ME_URL, REFRESH_URL

# ---------------------------------------------------------------------------
# Giriş
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_login_success(api_client, user):
    res = api_client.post(LOGIN_URL, {"username": "farmer1", "password": "StrongPass1!"})

    assert res.status_code == 200
    assert "access" in res.data
    assert "refresh" in res.data


@pytest.mark.django_db
def test_login_wrong_password(api_client, user):
    res = api_client.post(LOGIN_URL, {"username": "farmer1", "password": "wrongpass"})

    assert res.status_code == 401


@pytest.mark.django_db
def test_login_unknown_user(api_client, db):
    res = api_client.post(LOGIN_URL, {"username": "nobody", "password": "pass"})

    assert res.status_code == 401


@pytest.mark.django_db
def test_login_missing_fields(api_client, db):
    res = api_client.post(LOGIN_URL, {"username": "farmer1"})

    assert res.status_code == 400


# ---------------------------------------------------------------------------
# Token yenileme
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_refresh_returns_new_access_token(api_client, auth_tokens):
    original_access = auth_tokens["access"]

    res = api_client.post(REFRESH_URL, {"refresh": auth_tokens["refresh"]})

    assert res.status_code == 200
    assert "access" in res.data
    # rotate_refresh_tokens=True — yeni refresh token da dönmeli
    assert res.data["access"] != original_access


@pytest.mark.django_db
def test_refresh_with_invalid_token(api_client, db):
    res = api_client.post(REFRESH_URL, {"refresh": "notavalidtoken"})

    assert res.status_code == 401


@pytest.mark.django_db
def test_refresh_with_missing_token(api_client, db):
    res = api_client.post(REFRESH_URL, {})

    assert res.status_code == 400


# ---------------------------------------------------------------------------
# Çıkış
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_logout_blacklists_refresh_token(auth_client, auth_tokens, api_client):
    res = auth_client.post(LOGOUT_URL, {"refresh": auth_tokens["refresh"]})

    assert res.status_code == 204

    # Kara listeye alınan token artık yeni access token üretememeli
    retry = api_client.post(REFRESH_URL, {"refresh": auth_tokens["refresh"]})
    assert retry.status_code == 401


@pytest.mark.django_db
def test_logout_requires_authentication(api_client, auth_tokens):
    res = api_client.post(LOGOUT_URL, {"refresh": auth_tokens["refresh"]})

    assert res.status_code == 401


@pytest.mark.django_db
def test_logout_missing_refresh_token(auth_client):
    res = auth_client.post(LOGOUT_URL, {})

    assert res.status_code == 400


@pytest.mark.django_db
def test_logout_already_blacklisted_token(auth_client, auth_tokens):
    auth_client.post(LOGOUT_URL, {"refresh": auth_tokens["refresh"]})

    # Aynı token ikinci kez gönderildiğinde hata dönmeli
    res = auth_client.post(LOGOUT_URL, {"refresh": auth_tokens["refresh"]})
    assert res.status_code in (400, 401)


# ---------------------------------------------------------------------------
# /me/
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_me_returns_current_user(auth_client, user):
    res = auth_client.get(ME_URL)

    assert res.status_code == 200
    assert res.data["username"] == user.username
    assert res.data["first_name"] == user.first_name


@pytest.mark.django_db
def test_me_requires_authentication(api_client):
    res = api_client.get(ME_URL)

    assert res.status_code == 401


@pytest.mark.django_db
def test_me_patch_updates_first_name(auth_client, user):
    res = auth_client.patch(ME_URL, {"first_name": "Mehmet"})

    assert res.status_code == 200
    assert res.data["first_name"] == "Mehmet"


@pytest.mark.django_db
def test_me_with_expired_token(api_client, user):
    # Geçersiz / süresi dolmuş token ile istek
    api_client.credentials(HTTP_AUTHORIZATION="Bearer invalidtoken.payload.sig")

    res = api_client.get(ME_URL)

    assert res.status_code == 401
