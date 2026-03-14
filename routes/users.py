from flask import Blueprint, request, jsonify
from database.db_connection import db
from models.user_model import User
from services.reward_service import add_points

users_bp = Blueprint('users', __name__)

@users_bp.route('/register', methods=['POST'])
def register_user():
    data = request.json
    wallet_address = data.get('wallet_address')
    
    if not wallet_address:
        return jsonify({"error": "Wallet address is required"}), 400
    
    user = User.query.filter_by(wallet_address=wallet_address).first()
    if user:
        return jsonify(user.to_dict()), 200
    
    new_user = User(wallet_address=wallet_address)
    db.session.add(new_user)
    db.session.commit()
    
    # Award Signup Bonus
    add_points(wallet_address, 'signup_bonus')
    
    return jsonify(new_user.to_dict()), 201

@users_bp.route('/<wallet_address>', methods=['GET'])
def get_user_details(wallet_address):
    user = User.query.filter_by(wallet_address=wallet_address).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user.to_dict()), 200
