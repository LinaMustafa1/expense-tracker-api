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

    client.post(
        "/register",
        json={"email": "user2@test.com", "password": "Test1234"}
    )

    login1 = client.post(
        "/login",
        json={"email": "user1@test.com", "password": "Test1234"}
    )
    token1 = login1.get_json()["access_token"]

    login2 = client.post(
        "/login",
        json={"email": "user2@test.com", "password": "Test1234"}
    )
    token2 = login2.get_json()["access_token"]

    expense_response = client.post(
        "/expenses",
        headers={
            "Authorization": f"Bearer {token1}",
            "Idempotency-Key": "test-isolation-001"
        },
        json={
            "amount": 50,
            "category": "Food",
            "description": "Private expense"
        }
    )

    expense_id = expense_response.get_json()["id"]

    response = client.get(
        f"/expenses/{expense_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )

    assert response.status_code == 404


def test_expense_creation_is_idempotent():
    app = create_app()
    client = app.test_client()

    client.post(
        "/register",
        json={"email": "idempotent@test.com", "password": "Test1234"}
    )

    login = client.post(
        "/login",
        json={"email": "idempotent@test.com", "password": "Test1234"}
    )
    token = login.get_json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Idempotency-Key": "idempotent-test-002"
    }

    first = client.post(
        "/expenses",
        headers=headers,
        json={
            "amount": 25.50,
            "category": "Food",
            "description": "Lunch"
        }
    )

    second = client.post(
        "/expenses",
        headers=headers,
        json={
            "amount": 25.50,
            "category": "Food",
            "description": "Lunch"
        }
    )

    assert first.status_code == 201
    assert second.status_code == 200
    assert first.get_json()["id"] == second.get_json()["id"]
    assert second.get_json()["message"] == "original result returned"