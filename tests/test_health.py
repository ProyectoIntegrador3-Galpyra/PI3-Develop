import pytest


@pytest.mark.asyncio
async def test_health_ok(client):
    response = await client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "ok"
