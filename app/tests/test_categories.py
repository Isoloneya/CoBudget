def test_income_category_cannot_have_limit(client, owner_headers, budget_id):
    response = client.post(
        f"/budgets/{budget_id}/categories",
        json={"name": "Bonus", "type": "income", "limit_amount": 500},
        headers=owner_headers,
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_CATEGORY_LIMIT"


def test_expense_category_can_have_limit(client, owner_headers, budget_id):
    response = client.post(
        f"/budgets/{budget_id}/categories",
        json={"name": "Hobbies", "type": "expense", "limit_amount": 500},
        headers=owner_headers,
    )
    assert response.status_code == 201
    assert response.json()["limit_amount"] == "500.00"


def test_member_cannot_create_category(client, owner_headers, budget_id, make_user):
    invite = client.post(f"/budgets/{budget_id}/invites", headers=owner_headers).json()
    member_headers = make_user(email="member2@example.com")
    client.post(f"/invites/{invite['token']}/accept", headers=member_headers)

    response = client.post(
        f"/budgets/{budget_id}/categories",
        json={"name": "Should fail", "type": "expense"},
        headers=member_headers,
    )
    assert response.status_code == 403


def test_archiving_category_hides_it_from_default_list(client, owner_headers, budget_id):
    categories = client.get(f"/budgets/{budget_id}/categories", headers=owner_headers).json()
    category_id = categories[0]["id"]

    archive_response = client.delete(f"/budgets/{budget_id}/categories/{category_id}", headers=owner_headers)
    assert archive_response.status_code == 200
    assert archive_response.json()["is_archived"] is True

    remaining = client.get(f"/budgets/{budget_id}/categories", headers=owner_headers).json()
    assert category_id not in [c["id"] for c in remaining]