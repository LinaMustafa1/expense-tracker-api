from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Expense, IdempotencyKey

expenses_bp = Blueprint("expenses", __name__)


@expenses_bp.route("/expenses", methods=["POST"])
@jwt_required()
def create_expense():
    user_id = int(get_jwt_identity())

    idempotency_key = request.headers.get("Idempotency-Key")

    if not idempotency_key:
        return jsonify({"error": "Idempotency-Key header is required"}), 400

    existing_key = IdempotencyKey.query.filter_by(
        user_id=user_id,
        key=idempotency_key
    ).first()

    if existing_key:
        expense = Expense.query.get(existing_key.expense_id)

        return jsonify({
            "id": expense.id,
            "amount": expense.amount,
            "category": expense.category,
            "description": expense.description,
            "message": "original result returned"
        }), 200

    data = request.get_json()

    if not data:
        return jsonify({"error": "request body is required"}), 400

    amount = data.get("amount")
    category = data.get("category")
    description = data.get("description")

    if amount is None:
        return jsonify({"error": "amount is required"}), 400

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return jsonify({"error": "amount must be a number"}), 400

    if amount <= 0:
        return jsonify({"error": "amount must be greater than 0"}), 400

    if not category:
        return jsonify({"error": "category is required"}), 400

    expense = Expense(
        user_id=user_id,
        amount=amount,
        category=category,
        description=description
    )

    db.session.add(expense)
    db.session.flush()

    idempotency_record = IdempotencyKey(
        user_id=user_id,
        key=idempotency_key,
        expense_id=expense.id
    )

    db.session.add(idempotency_record)
    db.session.commit()

    return jsonify({
        "id": expense.id,
        "amount": expense.amount,
        "category": expense.category,
        "description": expense.description,
        "message": "expense created"
    }), 201


@expenses_bp.route("/expenses", methods=["GET"])
@jwt_required()
def get_expenses():
    user_id = int(get_jwt_identity())

    expenses = Expense.query.filter_by(user_id=user_id).all()

    return jsonify([
        {
            "id": expense.id,
            "amount": expense.amount,
            "category": expense.category,
            "description": expense.description,
            "created_at": expense.created_at.isoformat()
        }
        for expense in expenses
    ]), 200


@expenses_bp.route("/expenses/<int:expense_id>", methods=["GET"])
@jwt_required()
def get_expense(expense_id):
    user_id = int(get_jwt_identity())

    expense = Expense.query.filter_by(
        id=expense_id,
        user_id=user_id
    ).first()

    if not expense:
        return jsonify({"error": "expense not found"}), 404

    return jsonify({
        "id": expense.id,
        "amount": expense.amount,
        "category": expense.category,
        "description": expense.description,
        "created_at": expense.created_at.isoformat()
    }), 200


@expenses_bp.route("/expenses/<int:expense_id>", methods=["DELETE"])
@jwt_required()
def delete_expense(expense_id):
    user_id = int(get_jwt_identity())

    expense = Expense.query.filter_by(
        id=expense_id,
        user_id=user_id
    ).first()

    if not expense:
        return jsonify({"error": "expense not found"}), 404

    db.session.delete(expense)
    db.session.commit()

    return jsonify({"message": "expense deleted"}), 200