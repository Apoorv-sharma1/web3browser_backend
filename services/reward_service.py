from database.db_connection import db
from models.user_model import User
from models.reward_model import Reward
from datetime import datetime, date

def add_points(wallet_address, activity_type, score=0):
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
        # Check if reward was created today (naive UTC compare is usually fine for daily caps)
        if r.created_at.date() == today:
            points_earned_today += r.points
            
    DAILY_CAP = 50000 
    
    # Allow deductions (negative points) to always pass
    if points_earned_today >= DAILY_CAP and activity_type != 'signup_bonus' and not activity_type.endswith('_redemption'):
        return Reward(user_id=user.id, points=0, activity_type='cap_reached')

    points = 0
    if activity_type == 'dapp_interaction':
        points = 1 # 1pt per minute passive
    elif activity_type == 'login':
        points = 10
    elif activity_type == 'wtf_quest':
        points = 50
    elif activity_type == 'wtf_quest_action':
        # Reward scaled by performance
        points = max(5, int(score / 5)) 
    elif activity_type == 'node_referral':
        points = 50
    elif activity_type == 'signup_bonus':
        points = 3000
    elif activity_type.endswith('_redemption'):
        # For vouchers, score will be the negative cost
        points = -abs(score)
    elif activity_type == 'partner_cashback':
        points = 500
        
    # Apply global cap (except for signup bonus and deductions)
    if activity_type != 'signup_bonus' and not activity_type.endswith('_redemption') and points_earned_today + points > DAILY_CAP:
        points = DAILY_CAP - points_earned_today
    
    new_reward = Reward(user_id=user.id, points=points, activity_type=activity_type)
    db.session.add(new_reward)
    db.session.commit()
    return new_reward
