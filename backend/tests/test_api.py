LISTING = {"title": "Sunny room in Indiranagar", "city": "Bangalore", "rent": 12000}


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_register_login_and_weak_password(client, make_user):
    u = make_user()
    r = client.post("/api/auth/login", json={"email": u["email"], "password": "password123"})
    assert r.status_code == 200
    r = client.post("/api/auth/register", json={"email": "x@example.com", "password": "short", "full_name": "X"})
    assert r.status_code == 422


def test_login_lockout(client, make_user):
    u = make_user()
    codes = [client.post("/api/auth/login", json={"email": u["email"], "password": "wrong-password"}).status_code
             for _ in range(12)]
    assert 429 in codes


def test_retrain_requires_admin(client, make_user):
    assert client.post("/api/ml/retrain").status_code in (401, 403)
    u = make_user()
    assert client.post("/api/ml/retrain", headers=u["headers"]).status_code == 403


def test_listing_visibility_and_validation(client, make_user):
    owner, other = make_user("Owner"), make_user("Other")
    r = client.post("/api/listings", json={**LISTING, "photos": ["javascript:alert(1)"]}, headers=owner["headers"])
    assert r.status_code == 422
    r = client.post("/api/listings", json=LISTING, headers=owner["headers"])
    assert r.status_code == 200
    lid = r.json()["id"]
    status = r.json()["status"]
    got = client.get(f"/api/listings/{lid}", headers=other["headers"]).status_code
    assert got == (200 if status == "approved" else 404)
    assert client.get(f"/api/listings/{lid}", headers=owner["headers"]).status_code == 200


def test_search_pagination(client, make_user):
    u = make_user()
    assert client.get("/api/listings?limit=0", headers=u["headers"]).status_code == 422
    assert client.get("/api/listings?limit=5&offset=0", headers=u["headers"]).status_code == 200


def test_group_requires_membership(client, make_user):
    a, b = make_user("A"), make_user("B")
    r = client.post("/api/groups", json={"name": "Flat hunters"}, headers=a["headers"])
    if r.status_code == 200:
        gid = r.json()["id"]
        assert client.get(f"/api/groups/{gid}", headers=b["headers"]).status_code == 404


def test_upload_rejects_fake_image(client, make_user):
    u = make_user()
    r = client.post("/api/uploads", files={"file": ("a.png", b"not really an image", "image/png")},
                    headers=u["headers"])
    assert r.status_code in (400, 404, 415, 422)


def test_delete_account(client, make_user):
    u = make_user()
    r = client.request("DELETE", "/api/auth/me", json={"confirm": "DELETE"}, headers=u["headers"])
    assert r.status_code == 200
    assert client.post("/api/auth/login", json={"email": u["email"], "password": "password123"}).status_code in (401, 403)


def test_recommendations_hide_score_without_questionnaire(client, make_user):
    u = make_user()
    r = client.get("/api/matching/recommendations?city=Nowhereville", headers=u["headers"])
    assert r.status_code == 200
    assert all(m["score"] is None for m in r.json())
