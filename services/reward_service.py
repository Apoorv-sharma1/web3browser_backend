from database.db_connection import db
from models.user_model import User
from models.reward_model import Reward
from datetime import datetime, date

def add_points(wallet_address, activity_type):
    user = User.query.filter_by(wallet_address=wallet_address).first()
    if not user:
        return None
        
    today = date.today()
    
    # Calculate total points earned today
    todays_rewards = Reward.query.filter(
        Reward.user_id == user.id,
        Reward.points > 0
    ).all()
    
    points_earned_today = 0
    for r in todays_rewards:
        if r.created_at.date() == today:
            points_earned_today += r.points
            
    if points_earned_today >= 100:
        # Limit reached
        return Reward(user_id=user.id, points=0)

    # Check for specific wtf_quest daily limit (redundant now but keeps logic clean)
    if activity_type == 'wtf_quest':
        existing_quest = Reward.query.filter(
            Reward.user_id == user.id,
            Reward.points == 50
        ).all()
        
        for eq in existing_quest:
            if eq.created_at.date() == today:
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
        
    # Apply global cap
    if points_earned_today + points > 100:
        points = 100 - points_earned_today
    
    new_reward = Reward(user_id=user.id, points=points, activity_type=activity_type)
    db.session.add(new_reward)
    db.session.commit()
    return new_reward
