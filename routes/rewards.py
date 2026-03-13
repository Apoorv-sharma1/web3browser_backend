from flask import Blueprint, request, jsonify
from models.user_model import User
from models.reward_model import Reward
from services.reward_service import add_points

rewards_bp = Blueprint('rewards', __name__)

@rewards_bp.route('/claim', methods=['POST'])
def claim_reward():
    data = request.json
    wallet_address = data.get('wallet_address')
    
    # Simulate claiming activity recorded by frontend
    reward = add_points(wallet_address, 'dapp_interaction')
    if not reward:
        return jsonify({"error": "User not registered"}), 404
    
    return jsonify(reward.to_dict()), 200

@rewards_bp.route('/<wallet_address>', methods=['GET'])
def get_reward_history(wallet_address):
    user = User.query.filter_by(wallet_address=wallet_address).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    rewards = Reward.query.filter_by(user_id=user.id).all()
    return jsonify([r.to_dict() for r in rewards]), 200
