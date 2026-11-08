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


def test_bulk_import(client, make_user):
    u = make_user()
    csv_text = ("title,city,rent,amenities\n"
                "Cozy room,Ongole,4500,WiFi;Geyser\n"
                "x,Ongole,4500,\n"            # title too short
                "Big flat,Guntur,abc,\n")      # bad rent
    r = client.post("/api/listings/import", json={"csv": csv_text}, headers=u["headers"])
    assert r.status_code == 200
    body = r.json()
    assert body["created"] == 1 and len(body["errors"]) == 2
    mine = client.get("/api/listings/mine", headers=u["headers"]).json()
    assert any(l["title"] == "Cozy room" for l in mine)
    assert client.post("/api/listings/import", json={"csv": "foo,bar\n1,2"}, headers=u["headers"]).status_code == 400


ANS_A = {"cleanliness": 5, "sleep_time": "10 PM – 11 PM", "wake_time": "6 AM – 8 AM", "noise_tolerance": 2,
         "quiet_after": "Quiet after 10 PM", "smoking": "Never", "drinking": "Never", "food_pref": "Vegetarian",
         "guests": 2, "work_routine": 4, "social_pref": 2, "pets": "Open to pets"}
ANS_B = {**ANS_A, "cleanliness": 4, "noise_tolerance": 3}
ANS_C = {**ANS_A, "sleep_time": "After 2 AM", "wake_time": "After 10 AM", "smoking": "Regular", "cleanliness": 1,
         "noise_tolerance": 5, "quiet_after": "No preference"}


def _with_profile(client, u, answers):
    assert client.put("/api/profile/me", json={"full_name": "S" + str(u["id"]), "city": "Hyderabad"},
                      headers=u["headers"]).status_code == 200
    assert client.put("/api/profile/questionnaire", json={"answers": answers}, headers=u["headers"]).status_code == 200


def test_hostel_flow(client, make_user):
    staff, s1, s2, s3, outsider = (make_user("Warden"), make_user("S1"), make_user("S2"), make_user("S3"),
                                   make_user("Out"))
    for u, a in ((s1, ANS_A), (s2, ANS_B), (s3, ANS_C)):
        _with_profile(client, u, a)
    h = client.post("/api/hostels", json={"name": "Boys Hostel A", "room_size": 2}, headers=staff["headers"]).json()
    hid, code = h["id"], h["join_code"]

    # consent is required; wrong code is a 404; questionnaire must exist
    assert client.post("/api/hostels/join", json={"code": code, "consent": False}, headers=s1["headers"]).status_code == 400
    assert client.post("/api/hostels/join", json={"code": "ZZZZZZZZ", "consent": True}, headers=s1["headers"]).status_code == 404
    assert client.post("/api/hostels/join", json={"code": code, "consent": True}, headers=outsider["headers"]).status_code == 400
    for u in (s1, s2, s3):
        assert client.post("/api/hostels/join", json={"code": code, "block": "Block A", "consent": True},
                           headers=u["headers"]).status_code == 200

    # staff-only endpoints are hidden from students and strangers
    assert client.post(f"/api/hostels/{hid}/suggest", headers=s1["headers"]).status_code == 404
    assert client.get(f"/api/hostels/{hid}", headers=outsider["headers"]).status_code == 404

    assert client.post(f"/api/hostels/{hid}/suggest", headers=staff["headers"]).json()["suggested"] == 3
    d = client.get(f"/api/hostels/{hid}", headers=staff["headers"]).json()
    rooms = {r["room_no"]: [m["user_id"] for m in r["members"]] for r in d["rooms"]}
    assert sorted(len(v) for v in rooms.values()) == [1, 2]
    paired = next(v for v in rooms.values() if len(v) == 2)
    assert set(paired) == {s1["id"], s2["id"]}  # the two similar students share a room, not the night owl

    # students cannot see roommates until the institution finalises
    sv = client.get(f"/api/hostels/{hid}", headers=s1["headers"]).json()
    assert sv["roommates"] == [] and sv["my"]["room_no"] is None
    assert client.post(f"/api/hostels/{hid}/finalize", headers=staff["headers"]).status_code == 200
    sv = client.get(f"/api/hostels/{hid}", headers=s1["headers"]).json()
    assert len(sv["roommates"]) == 1 and sv["room_score"] is not None

    # change request -> staff approves -> student returns to the pool and allocation reopens
    assert client.post(f"/api/hostels/{hid}/change-requests", json={"reason": "Study schedule clash"},
                       headers=s1["headers"]).status_code == 200
    cr = client.get(f"/api/hostels/{hid}", headers=staff["headers"]).json()["change_requests"][0]
    assert client.patch(f"/api/hostels/{hid}/change-requests/{cr['id']}", json={"decision": "approve"},
                        headers=staff["headers"]).status_code == 200
    d = client.get(f"/api/hostels/{hid}", headers=staff["headers"]).json()
    assert any(u["user_id"] == s1["id"] for u in d["unassigned"]) and not d["hostel"]["allocation_final"]

    # insights are aggregate only; leaving deletes the student's membership
    ins = client.get(f"/api/hostels/{hid}/insights", headers=staff["headers"]).json()
    assert ins["students"] == 3 and "smoking" in ins["preferences"]
    assert client.delete(f"/api/hostels/{hid}/membership", headers=s3["headers"]).status_code == 200


def test_feedback_requires_accepted_connection(client, make_user):
    a, b = make_user("A"), make_user("B")
    _with_profile(client, a, ANS_A)
    _with_profile(client, b, ANS_B)
    assert client.post("/api/matching/connect", json={"recipient_id": b["id"]}, headers=a["headers"]).status_code == 200
    conns = client.get("/api/matching/connections", headers=a["headers"]).json()
    cid = conns[0]["id"]
    body = {"connection_id": cid, "fits": True, "outcome": "viewing"}
    assert client.post("/api/feedback", json=body, headers=a["headers"]).status_code == 404  # not accepted yet
    client.post(f"/api/matching/connections/{cid}/respond?action=accept", headers=b["headers"])
    assert client.post("/api/feedback", json=body, headers=a["headers"]).status_code == 200
    assert client.post("/api/feedback", json={**body, "outcome": "bogus"}, headers=a["headers"]).status_code == 400
    assert client.get("/api/feedback/mine", headers=a["headers"]).json()[str(cid)]["outcome"] == "viewing"


def test_recommendations_ranked_by_rules_score(client, make_user):
    me, close, far = make_user("Me"), make_user("Close"), make_user("Far")
    _with_profile(client, me, ANS_A)
    _with_profile(client, close, ANS_B)
    _with_profile(client, far, ANS_C)
    recs = client.get("/api/matching/recommendations?city=Hyderabad", headers=me["headers"]).json()
    scores = [r["score"] for r in recs]
    assert scores == sorted(scores, reverse=True) and all(r["ml_score"] is None for r in recs)


def test_demo_profiles_are_flagged(client, make_user):
    from app.database import SessionLocal
    from app.models import Profile, Questionnaire, User
    db = SessionLocal()
    demo = User(email="demo.testland@example.com", role="user")
    db.add(demo)
    db.flush()
    db.add(Profile(user_id=demo.id, full_name="Demo Person", city="Testland"))
    db.add(Questionnaire(user_id=demo.id, answers=ANS_A, completed_at=__import__("datetime").datetime.now()))
    db.commit()
    did = demo.id
    db.close()
    me = make_user("Viewer")
    _with_profile(client, me, ANS_A)
    recs = client.get("/api/matching/recommendations?city=Testland", headers=me["headers"]).json()
    assert any(r["user_id"] == did and r["is_demo"] for r in recs)
    assert client.get(f"/api/profile/{did}", headers=me["headers"]).json()["is_demo"] is True
    assert client.get(f"/api/profile/{me['id']}", headers=me["headers"]).json().get("is_demo") in (False, None)
