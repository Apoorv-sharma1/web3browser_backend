from flask import Blueprint, request, jsonify
from models.user_model import User
from models.reward_model import Reward
from database.db_connection import db
from services.reward_service import add_points

rewards_bp = Blueprint('rewards', __name__)

@rewards_bp.route('/claim', methods=['POST'])
def claim_reward():
    data = request.json
    wallet_address = data.get('wallet_address')
    activity_type = data.get('activity_type', 'dapp_interaction')
    
    # Simulate claiming activity recorded by frontend
    reward = add_points(wallet_address, activity_type)
    if not reward:
        return jsonify({"error": "User not registered"}), 404
    
    return jsonify(reward.to_dict()), 200

@rewards_bp.route('/redeem', methods=['POST'])
def redeem_points():
    data = request.json
    wallet_address = data.get('wallet_address')
    
    user = User.query.filter_by(wallet_address=wallet_address).first()
    if not user:
        return jsonify({"error": "User not registered"}), 404
        
    # Calculate current total points
    rewards = Reward.query.filter_by(user_id=user.id).all()
    total_points = sum(r.points for r in rewards)
    
    if total_points < 1000:
        return jsonify({"error": "Insufficient points"}), 400
        
    # Deduct points, add token
    new_reward = Reward(user_id=user.id, points=-1000, token_amount=1.0)
    db.session.add(new_reward)
    db.session.commit()
    
    return jsonify(new_reward.to_dict()), 200

@rewards_bp.route('/<wallet_address>', methods=['GET'])
def get_reward_history(wallet_address):
    user = User.query.filter_by(wallet_address=wallet_address).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    rewards = Reward.query.filter_by(user_id=user.id).all()
    return jsonify([r.to_dict() for r in rewards]), 200
