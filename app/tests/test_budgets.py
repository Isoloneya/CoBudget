def test_create_budget_makes_creator_owner(client, owner_headers):
    response = client.post("/budgets", json={"name": "My Budget"}, headers=owner_headers)
    assert response.status_code == 201
    assert response.json()["role"] == "owner"


def test_create_budget_seeds_default_categories(client, owner_headers, budget_id):
    response = client.get(f"/budgets/{budget_id}/categories", headers=owner_headers)
    assert response.status_code == 200
    categories = response.json()
    assert len(categories) == 10
    assert all(c["limit_amount"] is None for c in categories)


def test_non_member_cannot_view_budget(client, owner_headers, budget_id, make_user):
    outsider_headers = make_user(email="outsider@example.com")
    response = client.get(f"/budgets/{budget_id}", headers=outsider_headers)
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"


def test_nonexistent_budget_returns_404(client, owner_headers):
    response = client.get("/budgets/00000000-0000-0000-0000-000000000000", headers=owner_headers)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "BUDGET_NOT_FOUND"


def test_only_owner_can_update_budget(client, owner_headers, budget_id, make_user):
    invite = client.post(f"/budgets/{budget_id}/invites", headers=owner_headers).json()
    member_headers = make_user(email="member@example.com")
    client.post(f"/invites/{invite['token']}/accept", headers=member_headers)

    response = client.patch(f"/budgets/{budget_id}", json={"name": "Hacked"}, headers=member_headers)
    assert response.status_code == 403


def test_deleting_budget_cascades_categories(client, owner_headers, budget_id):
    delete_response = client.delete(f"/budgets/{budget_id}", headers=owner_headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/budgets/{budget_id}", headers=owner_headers)
    assert get_response.status_code == 404