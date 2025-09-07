# models.py - Extended version with rewards configuration tables

from . import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    user_id                    = db.Column(db.Integer, primary_key=True)
    shopify_customer_id        = db.Column(db.String(255), nullable=True)
    first_name                 = db.Column(db.String(255), nullable=True)
    last_name                  = db.Column(db.String(255), nullable=True)
    email                      = db.Column(db.String(255), unique=True, nullable=False)
    date_of_birth              = db.Column(db.Date, nullable=True)
    membership_status          = db.Column(db.String(50), nullable=True)
    vip_tier_name              = db.Column(db.String(100), nullable=True)

    points                     = db.Column(db.Integer, default=0, nullable=False)
    referral_count             = db.Column(db.Integer, default=0, nullable=False)
    referral_purchases_count   = db.Column(db.Integer, default=0, nullable=False)

    referral_code              = db.Column(db.String(50), unique=True, nullable=True)
    referal_discount_code      = db.Column(db.JSON, nullable=True, default=dict)
    discount_code_id           = db.Column(db.Integer, nullable=True)

    referred_by                = db.Column(db.String(50), nullable=True)
    last_discount_code         = db.Column(db.String(50), nullable=True)

    created_at                 = db.Column(
                                   db.DateTime,
                                   server_default=db.func.now(),
                                   nullable=False
                                 )

# New table for program configuration
class ProgramConfig(db.Model):
    __tablename__ = 'program_config'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)  # e.g., 'referral_give_amount'
    value = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    data_type = db.Column(db.String(50), default='string')  # string, integer, boolean, json
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.String(100), nullable=True)

# Table for managing rewards (the redemption options)
class Reward(db.Model):
    __tablename__ = 'rewards'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # e.g., "$5 off coupon"
    points_required = db.Column(db.Integer, nullable=False)  # e.g., 500
    reward_value = db.Column(db.String(100), nullable=False)  # e.g., "5CAD" or "dynamic"
    reward_type = db.Column(db.String(50), default='discount')  # discount, product, shipping
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)  # for sorting in UI
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Table for managing earning actions
class EarnAction(db.Model):
    __tablename__ = 'earn_actions'
    
    id = db.Column(db.Integer, primary_key=True)
    action_key = db.Column(db.String(100), unique=True, nullable=False)  # e.g., 'instagram_follow'
    name = db.Column(db.String(200), nullable=False)  # e.g., "Follow on Instagram"
    points_awarded = db.Column(db.Integer, nullable=False)  # e.g., 50
    action_type = db.Column(db.String(50), default='social')  # social, purchase, signup, etc.
    action_url = db.Column(db.String(500), nullable=True)  # e.g., Instagram URL
    icon = db.Column(db.String(50), nullable=True)  # icon identifier
    is_active = db.Column(db.Boolean, default=True)
    is_repeatable = db.Column(db.Boolean, default=False)  # can user do it multiple times?
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Track which users have completed which actions
class UserEarnedAction(db.Model):
    __tablename__ = 'user_earned_actions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    action_id = db.Column(db.Integer, db.ForeignKey('earn_actions.id'), nullable=False)
    points_earned = db.Column(db.Integer, nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='earned_actions')
    action = db.relationship('EarnAction', backref='user_completions')
