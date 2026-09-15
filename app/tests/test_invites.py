def test_invite_accept_creates_member(client, owner_headers, budget_id, make_user):
    invite = client.post(f"/budgets/{budget_id}/invites", headers=owner_headers).json()
    member_headers = make_user(email="joiner@example.com")

    response = client.post(f"/invites/{invite['token']}/accept", headers=member_headers)
    assert response.status_code == 200
    assert response.json()["role"] == "member"

    members = client.get(f"/budgets/{budget_id}/members", headers=owner_headers).json()
    assert any(m["email"] == "joiner@example.com" for m in members)


def test_invite_cannot_be_used_twice(client, owner_headers, budget_id, make_user):
    invite = client.post(f"/budgets/{budget_id}/invites", headers=owner_headers).json()
    first_user = make_user(email="joiner1@example.com")
    second_user = make_user(email="joiner2@example.com")

    client.post(f"/invites/{invite['token']}/accept", headers=first_user)
    response = client.post(f"/invites/{invite['token']}/accept", headers=second_user)

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_INVITE_TOKEN"


def test_invalid_token_returns_400(client, owner_headers, make_user):
    member_headers = make_user(email="joiner3@example.com")
    response = client.post("/invites/not-a-real-token/accept", headers=member_headers)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_INVITE_TOKEN"


def test_member_cannot_create_invite(client, owner_headers, budget_id, make_user):
    invite = client.post(f"/budgets/{budget_id}/invites", headers=owner_headers).json()
    member_headers = make_user(email="joiner4@example.com")
    client.post(f"/invites/{invite['token']}/accept", headers=member_headers)

    response = client.post(f"/budgets/{budget_id}/invites", headers=member_headers)
    assert response.status_code == 403