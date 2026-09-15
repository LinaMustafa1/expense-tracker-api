import uuid

import pytest
from app import create_app


def test_expenses_requires_authentication():
    app = create_app()
    client = app.test_client()

    response = client.get("/expenses")

    assert response.status_code == 401


def test_user_cannot_read_another_users_expense():
    app = create_app()
    client = app.test_client()

    client.post(
        "/register",
        json={"email": "user1@test.com", "password": "Test1234"}
    )

    login1 = client.post(
        "/login",
        json={"email": "user1@test.com", "password": "Test1234"}
    )
    token1 = login1.get_json()["access_token"]

    client.post(
        "/expenses",
        headers={
            "Authorization": f"Bearer {token1}",
            "Idempotency-Key": "user1-expense-001"
        },
        json={
            "amount": 50,
            "category": "Food",
            "description": "User 1 expense"
        }
    )

    client.post(
        "/register",
        json={"email": "user2@test.com", "password": "Test1234"}
    )

    login2 = client.post(
        "/login",
        json={"email": "user2@test.com", "password": "Test1234"}
    )
    token2 = login2.get_json()["access_token"]

    response = client.get(
        "/expenses",
        headers={"Authorization": f"Bearer {token2}"}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert all(
        expense.get("description") != "User 1 expense"
        for expense in data
    )


def test_expense_creation_is_idempotent():
    app = create_app()
    client = app.test_client()

    email = f"idempotent-{uuid.uuid4()}@test.com"
    idempotency_key = f"idempotent-{uuid.uuid4()}"

    client.post(
        "/register",
        json={"email": email, "password": "Test1234"}
    )

    login = client.post(
        "/login",
        json={"email": email, "password": "Test1234"}
    )
    token = login.get_json()["access_token"]

    payload = {
        "amount": 25,
        "category": "Food",
        "description": "Idempotent expense"
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Idempotency-Key": idempotency_key
    }

    first = client.post(
        "/expenses",
        headers=headers,
        json=payload
    )

    second = client.post(
        "/expenses",
        headers=headers,
        json=payload
    )

    assert first.status_code == 201
    assert second.status_code == 200

    first_data = first.get_json()
    second_data = second.get_json()

    assert second_data["id"] == first_data["id"]
    assert second_data["amount"] == first_data["amount"]
    assert second_data["category"] == first_data["category"]
    assert second_data["description"] == first_data["description"]


def test_expense_rejects_invalid_amount():
    app = create_app()
    client = app.test_client()

    client.post(
        "/register",
        json={"email": "invalid@test.com", "password": "Test1234"}
    )

    login = client.post(
        "/login",
        json={"email": "invalid@test.com", "password": "Test1234"}
    )
    token = login.get_json()["access_token"]

    response = client.post(
        "/expenses",
        headers={
            "Authorization": f"Bearer {token}",
            "Idempotency-Key": "invalid-amount-test-001"
        },
        json={
            "amount": "not-a-number",
            "category": "Food",
            "description": "Invalid expense"
        }
    )

    assert response.status_code == 400


def test_expense_rejects_missing_amount():
    app = create_app()
    client = app.test_client()

    client.post(
        "/register",
        json={
            "email": "missingamount@test.com",
            "password": "Test1234"
        }
    )

    login = client.post(
        "/login",
        json={
            "email": "missingamount@test.com",
            "password": "Test1234"
        }
    )
    token = login.get_json()["access_token"]

    response = client.post(
        "/expenses",
        headers={
            "Authorization": f"Bearer {token}",
            "Idempotency-Key": "missing-amount-test-001"
        },
        json={
            "category": "Food",
            "description": "Missing amount"
        }
    )

    assert response.status_code == 400