# Expense Tracker API

A REST API for managing personal expenses, built with Python, Flask, PostgreSQL, SQLAlchemy, and JWT authentication.

## Features

* User registration and login
* JWT-based authentication
* Create, view, and delete expenses
* Users can only access their own expenses
* Idempotent expense creation using the `Idempotency-Key` header
* Clear validation and error messages
* Automated tests with pytest

## Tech Stack

* Python
* Flask
* PostgreSQL
* Flask-SQLAlchemy
* Flask-JWT-Extended
* pytest

## API Endpoints

| Method | Endpoint         | Authentication | Description                               |
| ------ | ---------------- | -------------- | ----------------------------------------- |
| POST   | `/register`      | No             | Create a new user                         |
| POST   | `/login`         | No             | Login and receive a JWT token             |
| POST   | `/expenses`      | Yes            | Create an expense                         |
| GET    | `/expenses`      | Yes            | Get the current user's expenses           |
| GET    | `/expenses/<id>` | Yes            | Get one of the current user's expenses    |
| DELETE | `/expenses/<id>` | Yes            | Delete one of the current user's expenses |

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd expense-tracker-api
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/expense_tracker
JWT_SECRET_KEY=your-secret-key
```

Do not commit `.env` or real secrets to the repository.

### 5. Run the API

```bash
python app.py
```

The API will run locally at:

```text
http://127.0.0.1:5000
```

## Authentication

Register a user with:

```http
POST /register
```

Example:

```json
{
  "email": "user@example.com",
  "password": "Test1234"
}
```

Login with:

```http
POST /login
```

The response contains an `access_token`.

For protected endpoints, send:

```http
Authorization: Bearer <access_token>
```

## Creating an Expense

To create an expense:

```http
POST /expenses
```

The request must include an `Idempotency-Key` header.

Example:

```text
Idempotency-Key: expense-001
```

Example request body:

```json
{
  "amount": 25.50,
  "category": "Food",
  "description": "Lunch"
}
```

## Idempotency

Expense creation is retry-safe through the `Idempotency-Key` header.

For each authenticated user, the combination of:

```text
user_id + Idempotency-Key
```

must be unique.

If the same user sends the same create request again with the same idempotency key, the API returns the original expense instead of creating a duplicate row.

The first request returns:

```text
201 Created
```

A repeated request with the same key returns:

```text
200 OK
```

with:

```json
{
  "message": "original result returned"
}
```

## User Isolation

Expenses belong to the authenticated user who created them.

A user cannot access another user's expense, even if they know its ID.

The API filters expense queries by both:

```text
expense_id
user_id
```

Unauthorized access to another user's expense returns:

```text
404 Not Found
```

## Error Handling

The API returns clear validation errors.

For example, creating an expense without an amount returns:

```json
{
  "error": "amount is required"
}
```

Protected endpoints without authentication return:

```text
401 Unauthorized
```

## Testing

Run the automated tests with:

```bash
python -m pytest
```

The test suite verifies:

* Protected routes require authentication
* Users cannot access another user's expenses
* Expense creation is idempotent

## Security

* Passwords are stored as password hashes, not plain text.
* JWT authentication protects private endpoints.
* Environment variables are used for database credentials and JWT secrets.
* `.env` is excluded from version control.
* Users can only access their own expense records.
