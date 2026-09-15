from datetime import date, timedelta


def _category_id(client, headers, budget_id, name):
    categories = client.get(f"/budgets/{budget_id}/categories", headers=headers).json()
    return next(c["id"] for c in categories if c["name"] == name)


def test_transaction_type_is_derived_from_category(client, owner_headers, budget_id):
    salary_id = _category_id(client, owner_headers, budget_id, "Зарплата")

    response = client.post(
        f"/budgets/{budget_id}/transactions",
        json={"amount": 1000, "category_id": salary_id, "txn_date": str(date.today())},
        headers=owner_headers,
    )
    assert response.status_code == 201
    assert response.json()["type"] == "income"


def test_transaction_date_cannot_be_in_future(client, owner_headers, budget_id):
    groceries_id = _category_id(client, owner_headers, budget_id, "Продукти")
    tomorrow = str(date.today() + timedelta(days=1))

    response = client.post(
        f"/budgets/{budget_id}/transactions",
        json={"amount": 100, "category_id": groceries_id, "txn_date": tomorrow},
        headers=owner_headers,
    )
    assert response.status_code == 422


def test_transaction_amount_must_be_positive(client, owner_headers, budget_id):
    groceries_id = _category_id(client, owner_headers, budget_id, "Продукти")

    response = client.post(
        f"/budgets/{budget_id}/transactions",
        json={"amount": -50, "category_id": groceries_id, "txn_date": str(date.today())},
        headers=owner_headers,
    )
    assert response.status_code == 422


def test_category_from_another_budget_is_rejected(client, owner_headers, budget_id):
    other_budget = client.post("/budgets", json={"name": "Other"}, headers=owner_headers).json()
    other_category_id = _category_id(client, owner_headers, other_budget["id"], "Продукти")

    response = client.post(
        f"/budgets/{budget_id}/transactions",
        json={"amount": 100, "category_id": other_category_id, "txn_date": str(date.today())},
        headers=owner_headers,
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "CATEGORY_NOT_FOUND"


def test_member_cannot_edit_others_transaction(client, owner_headers, budget_id, make_user):
    groceries_id = _category_id(client, owner_headers, budget_id, "Продукти")
    transaction = client.post(
        f"/budgets/{budget_id}/transactions",
        json={"amount": 100, "category_id": groceries_id, "txn_date": str(date.today())},
        headers=owner_headers,
    ).json()

    invite = client.post(f"/budgets/{budget_id}/invites", headers=owner_headers).json()
    member_headers = make_user(email="member3@example.com")
    client.post(f"/invites/{invite['token']}/accept", headers=member_headers)

    response = client.patch(
        f"/budgets/{budget_id}/transactions/{transaction['id']}",
        json={"comment": "hijacked"},
        headers=member_headers,
    )
    assert response.status_code == 403


def test_owner_can_edit_members_transaction(client, owner_headers, budget_id, make_user):
    invite = client.post(f"/budgets/{budget_id}/invites", headers=owner_headers).json()
    member_headers = make_user(email="member4@example.com")
    client.post(f"/invites/{invite['token']}/accept", headers=member_headers)

    groceries_id = _category_id(client, owner_headers, budget_id, "Продукти")
    transaction = client.post(
        f"/budgets/{budget_id}/transactions",
        json={"amount": 100, "category_id": groceries_id, "txn_date": str(date.today())},
        headers=member_headers,
    ).json()

    response = client.patch(
        f"/budgets/{budget_id}/transactions/{transaction['id']}",
        json={"comment": "owner override"},
        headers=owner_headers,
    )
    assert response.status_code == 200
    assert response.json()["comment"] == "owner override"


def test_summary_reflects_balance_and_over_limit_status(client, owner_headers, budget_id):
    salary_id = _category_id(client, owner_headers, budget_id, "Зарплата")
    groceries_id = _category_id(client, owner_headers, budget_id, "Продукти")

    client.patch(f"/budgets/{budget_id}/categories/{groceries_id}", json={"limit_amount": 100}, headers=owner_headers)
    client.post(
        f"/budgets/{budget_id}/transactions",
        json={"amount": 5000, "category_id": salary_id, "txn_date": str(date.today())},
        headers=owner_headers,
    )
    client.post(
        f"/budgets/{budget_id}/transactions",
        json={"amount": 150, "category_id": groceries_id, "txn_date": str(date.today())},
        headers=owner_headers,
    )

    summary = client.get(f"/budgets/{budget_id}/summary", headers=owner_headers).json()
    assert summary["income_total"] == "5000.00"
    assert summary["expense_total"] == "150.00"
    assert summary["balance"] == "4850.00"

    groceries_summary = next(c for c in summary["categories"] if c["id"] == groceries_id)
    assert groceries_summary["status"] == "over"