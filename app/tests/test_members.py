def _join_as_member(client, owner_headers, budget_id, make_user, email):
    invite = client.post(f"/budgets/{budget_id}/invites", headers=owner_headers).json()
    member_headers = make_user(email=email)
    accepted = client.post(f"/invites/{invite['token']}/accept", headers=member_headers).json()
    return member_headers, accepted


def test_cannot_remove_last_owner(client, owner_headers, budget_id):
    members = client.get(f"/budgets/{budget_id}/members", headers=owner_headers).json()
    owner_user_id = members[0]["user_id"]

    response = client.delete(f"/budgets/{budget_id}/members/{owner_user_id}", headers=owner_headers)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "CANNOT_REMOVE_LAST_OWNER"


def test_cannot_demote_last_owner(client, owner_headers, budget_id):
    members = client.get(f"/budgets/{budget_id}/members", headers=owner_headers).json()
    owner_user_id = members[0]["user_id"]

    response = client.patch(
        f"/budgets/{budget_id}/members/{owner_user_id}", json={"role": "member"}, headers=owner_headers
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "CANNOT_REMOVE_LAST_OWNER"


def test_owner_can_remove_member(client, owner_headers, budget_id, make_user):
    _join_as_member(client, owner_headers, budget_id, make_user, "removable@example.com")

    members = client.get(f"/budgets/{budget_id}/members", headers=owner_headers).json()
    removable = next(m for m in members if m["email"] == "removable@example.com")

    response = client.delete(f"/budgets/{budget_id}/members/{removable['user_id']}", headers=owner_headers)
    assert response.status_code == 204

    members_after = client.get(f"/budgets/{budget_id}/members", headers=owner_headers).json()
    assert not any(m["email"] == "removable@example.com" for m in members_after)


def test_member_cannot_change_roles(client, owner_headers, budget_id, make_user):
    member_headers, _ = _join_as_member(client, owner_headers, budget_id, make_user, "nopriv@example.com")
    members = client.get(f"/budgets/{budget_id}/members", headers=owner_headers).json()
    owner_user_id = next(m["user_id"] for m in members if m["role"] == "owner")

    response = client.patch(
        f"/budgets/{budget_id}/members/{owner_user_id}", json={"role": "member"}, headers=member_headers
    )
    assert response.status_code == 403