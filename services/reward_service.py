from database.db_connection import db
from models.user_model import User
from models.reward_model import Reward
from datetime import datetime, date

def add_points(wallet_address, activity_type):
    user = User.query.filter_by(wallet_address=wallet_address).first()
    if not user:
        return None
        
    # Check for daily wtf_quest limit
    if activity_type == 'wtf_quest':
        today = date.today()
        # Find if the user already did wtf_quest today
        existing_quest = Reward.query.filter(
            Reward.user_id == user.id,
            Reward.points == 50  # This relies on the fact that wtf_quest is 50 pts, but normally we'd track activity_type in the DB.
        ).all()
        
        # Since we don't store activity_type explicitly on Reward yet, we check timestamp dates
        for eq in existing_quest:
            if eq.timestamp.date() == today:
                # Quest already completed today
                return None
    
    points = 0
    if activity_type == 'dapp_interaction':
        points = 20
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
