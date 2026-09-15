# Expense Tracker API

A REST API for managing personal expenses with user authentication, expense tracking, input validation, and idempotent expense creation.

## Features

* User registration and login
* JWT-based authentication
* Create and view expenses
* Users can only access their own expenses
* Input validation with clear `400` responses
* Idempotent expense creation using an `Idempotency-Key`
* Automated API tests with pytest

## API Endpoints

### Authentication

* `POST /register` — Create a new user
* `POST /login` — Log in and receive an access token

### Expenses

* `POST /expenses` — Create an expense
* `GET /expenses` — Get the authenticated user's expenses

Expense creation requires authentication and an `Idempotency-Key`.

## Validation

The API rejects invalid or incomplete expense data with a `400` response instead of returning a server error.

Examples include:

* Invalid expense amounts
* Missing required fields

## Idempotency

Creating an expense with the same `Idempotency-Key` returns the existing expense instead of creating a duplicate.

This makes repeated requests safe to retry.

## Running the Project

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

## Running Tests

Run the test suite with:

```bash
pytest
```

The tests cover authentication, user data isolation, idempotent expense creation, and invalid or missing expense data.

API documentation and testing information are included in this README.