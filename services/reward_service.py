from database.db_connection import db
from models.user_model import User
from models.reward_model import Reward

def add_points(wallet_address, activity_type):
    user = User.query.filter_by(wallet_address=wallet_address).first()
    if not user:
        return None
    
    points = 0
    if activity_type == 'dapp_interaction':
        points = 50
    elif activity_type == 'login':
        points = 10
    elif activity_type == 'wtf_quest':
        points = 50
    elif activity_type == 'wtf_quest_action':
        points = 5
    elif activity_type == 'node_referral':
        points = 50
    elif activity_type == 'partner_cashback':
        points = 500
    
    new_reward = Reward(user_id=user.id, points=points)
    db.session.add(new_reward)
    db.session.commit()
    return new_reward
