import os
import tempfile

_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"
os.environ["ENV"] = "development"
os.environ["JWT_SECRET"] = "test-secret-key-that-is-long-enough-123"
os.environ["SEED_DEMO"] = "false"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.services import ratelimit  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def _reset_limits():
    ratelimit.reset()
    yield


_n = {"i": 0}


@pytest.fixture
def make_user(client):
    def _make(name="Test User"):
        _n["i"] += 1
        email = f"user{_n['i']}@example.com"
        r = client.post("/api/auth/register", json={"email": email, "password": "password123", "full_name": name})
        assert r.status_code == 200, r.text
        tok = r.json()["access_token"]
        return {"email": email, "headers": {"Authorization": f"Bearer {tok}"}, "id": r.json()["user"]["id"]}
    return _make
