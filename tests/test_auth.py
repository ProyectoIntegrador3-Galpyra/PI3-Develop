import pytest


@pytest.mark.asyncio
async def test_login_refresh_logout(client, seeded_admin):
    login_response = await client.post(
        "/api/auth/login",
        json={"email": seeded_admin.email, "password": "Admin123*"},
    )

    assert login_response.status_code == 200
    login_body = login_response.json()
    assert login_body["success"] is True
    assert login_body["data"]["access_token"]
    assert login_body["data"]["refresh_token"]

    refresh_response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": login_body["data"]["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    refresh_body = refresh_response.json()
    assert refresh_body["success"] is True

    logout_response = await client.post(
        "/api/auth/logout",
        json={"refresh_token": refresh_body["data"]["refresh_token"]},
    )
    assert logout_response.status_code == 200
    assert logout_response.json()["success"] is True
