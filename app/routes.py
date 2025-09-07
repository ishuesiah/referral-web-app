# routes.py - Extended with rewards management features

import os
import time
import bcrypt
import json
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from functools import wraps
from .models import User, ProgramConfig, Reward, EarnAction, UserEarnedAction
from . import db

bp = Blueprint('main', __name__)

# Load the bcrypt hash from environment (must be set as raw bytes)
PASSWORD_HASH = os.getenv('ADMIN_PASSWORD', '').encode()

@bp.route('/health')
def health():
    return "OK", 200

@bp.route('/', methods=['GET', 'POST'])
def login():
    error_msg = None
    if request.method == "POST":
        entered = request.form.get("password", "").encode()
        if PASSWORD_HASH and bcrypt.checkpw(entered, PASSWORD_HASH):
            session.clear()
            session['authenticated'] = True
            session['last_active'] = time.time()
            return redirect(url_for('main.list_users'))
        else:
            error_msg = "Invalid password. Please try again."
    return render_template('login.html', error=error_msg)

# Decorator to protect routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('main.login'))
        # Optionally check last_active for session timeout here
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/users')
@login_required
def list_users():
    q = request.args.get('q', '')
    sort = request.args.get('sort', 'newest')  # default to newest
    page = request.args.get('page', 1, type=int)
    per_page = 300

    query = User.query
    if q:
        query = query.filter(
            (User.first_name.ilike(f'%{q}%')) |
            (User.email.ilike(f'%{q}%')) |
            (User.referral_code.ilike(f'%{q}%'))
        )

    # Apply sort order
    if sort == 'oldest':
        query = query.order_by(User.created_at.asc())
    else:  # newest
        query = query.order_by(User.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        'users.html',
        users=pagination.items,
        q=q,
        sort=sort,
        pagination=pagination
    )

@bp.route('/users/<int:user_id>/points', methods=['POST'])
@login_required
def update_points(user_id):
    amount = int(request.form.get('amount', 0))
    user = User.query.get_or_404(user_id)
    user.points = max(0, user.points + amount)
    db.session.commit()
    flash(f'Updated points for {user.email}. New balance: {user.points}', 'success')
    return redirect(url_for('main.list_users', page=request.args.get('page', 1), q=request.args.get('q', '')))

# ============== REWARDS CONFIGURATION ROUTES ==============

@bp.route('/settings')
@login_required
def settings():
    """Main settings page for rewards program configuration"""
    # Get all config values
    configs = ProgramConfig.query.all()
    config_dict = {c.key: c for c in configs}
    
    # Set defaults if not exist
    default_configs = [
        ('referral_give_amount', '15', 'Amount friend gets when using referral link (in CAD)'),
        ('referral_get_amount', '15', 'Amount referrer gets when friend makes purchase (in CAD)'),
        ('signup_bonus_points', '100', 'Points awarded for signing up'),
        ('points_per_dollar', '5', 'Points earned per dollar spent'),
        ('referral_goal', '50', 'Target number of referrals for progress bar'),
    ]
    
    for key, default_value, description in default_configs:
        if key not in config_dict:
            config = ProgramConfig(key=key, value=default_value, description=description)
            db.session.add(config)
            config_dict[key] = config
    
    db.session.commit()
    
    return render_template('settings.html', configs=config_dict)

@bp.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    """Update program configuration values"""
    for key, value in request.form.items():
        if key.startswith('config_'):
            config_key = key.replace('config_', '')
            config = ProgramConfig.query.filter_by(key=config_key).first()
            if config:
                config.value = value
                config.updated_by = session.get('username', 'admin')
    
    db.session.commit()
    flash('Settings updated successfully!', 'success')
    return redirect(url_for('main.settings'))

# ============== REWARDS MANAGEMENT ROUTES ==============

@bp.route('/rewards')
@login_required
def manage_rewards():
    """List all rewards"""
    rewards = Reward.query.order_by(Reward.display_order, Reward.points_required).all()
    return render_template('rewards.html', rewards=rewards)

@bp.route('/rewards/add', methods=['GET', 'POST'])
@login_required
def add_reward():
    """Add a new reward"""
    if request.method == 'POST':
        reward = Reward(
            name=request.form.get('name'),
            points_required=int(request.form.get('points_required')),
            reward_value=request.form.get('reward_value'),
            reward_type=request.form.get('reward_type', 'discount'),
            description=request.form.get('description'),
            is_active=request.form.get('is_active') == 'on',
            display_order=int(request.form.get('display_order', 0))
        )
        db.session.add(reward)
        db.session.commit()
        flash(f'Reward "{reward.name}" added successfully!', 'success')
        return redirect(url_for('main.manage_rewards'))
    
    return render_template('reward_form.html', reward=None)

@bp.route('/rewards/<int:reward_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_reward(reward_id):
    """Edit an existing reward"""
    reward = Reward.query.get_or_404(reward_id)
    
    if request.method == 'POST':
        reward.name = request.form.get('name')
        reward.points_required = int(request.form.get('points_required'))
        reward.reward_value = request.form.get('reward_value')
        reward.reward_type = request.form.get('reward_type', 'discount')
        reward.description = request.form.get('description')
        reward.is_active = request.form.get('is_active') == 'on'
        reward.display_order = int(request.form.get('display_order', 0))
        
        db.session.commit()
        flash(f'Reward "{reward.name}" updated successfully!', 'success')
        return redirect(url_for('main.manage_rewards'))
    
    return render_template('reward_form.html', reward=reward)

@bp.route('/rewards/<int:reward_id>/delete', methods=['POST'])
@login_required
def delete_reward(reward_id):
    """Delete a reward"""
    reward = Reward.query.get_or_404(reward_id)
    db.session.delete(reward)
    db.session.commit()
    flash(f'Reward "{reward.name}" deleted successfully!', 'success')
    return redirect(url_for('main.manage_rewards'))

# ============== EARN ACTIONS MANAGEMENT ROUTES ==============

@bp.route('/earn-actions')
@login_required
def manage_earn_actions():
    """List all earning actions"""
    actions = EarnAction.query.order_by(EarnAction.display_order, EarnAction.name).all()
    return render_template('earn_actions.html', actions=actions)

@bp.route('/earn-actions/add', methods=['GET', 'POST'])
@login_required
def add_earn_action():
    """Add a new earning action"""
    if request.method == 'POST':
        action = EarnAction(
            action_key=request.form.get('action_key'),
            name=request.form.get('name'),
            points_awarded=int(request.form.get('points_awarded')),
            action_type=request.form.get('action_type', 'social'),
            action_url=request.form.get('action_url'),
            icon=request.form.get('icon'),
            is_active=request.form.get('is_active') == 'on',
            is_repeatable=request.form.get('is_repeatable') == 'on',
            display_order=int(request.form.get('display_order', 0))
        )
        db.session.add(action)
        db.session.commit()
        flash(f'Action "{action.name}" added successfully!', 'success')
        return redirect(url_for('main.manage_earn_actions'))
    
    return render_template('earn_action_form.html', action=None)

@bp.route('/earn-actions/<int:action_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_earn_action(action_id):
    """Edit an existing earning action"""
    action = EarnAction.query.get_or_404(action_id)
    
    if request.method == 'POST':
        action.action_key = request.form.get('action_key')
        action.name = request.form.get('name')
        action.points_awarded = int(request.form.get('points_awarded'))
        action.action_type = request.form.get('action_type', 'social')
        action.action_url = request.form.get('action_url')
        action.icon = request.form.get('icon')
        action.is_active = request.form.get('is_active') == 'on'
        action.is_repeatable = request.form.get('is_repeatable') == 'on'
        action.display_order = int(request.form.get('display_order', 0))
        
        db.session.commit()
        flash(f'Action "{action.name}" updated successfully!', 'success')
        return redirect(url_for('main.manage_earn_actions'))
    
    return render_template('earn_action_form.html', action=action)

@bp.route('/earn-actions/<int:action_id>/delete', methods=['POST'])
@login_required
def delete_earn_action(action_id):
    """Delete an earning action"""
    action = EarnAction.query.get_or_404(action_id)
    db.session.delete(action)
    db.session.commit()
    flash(f'Action "{action.name}" deleted successfully!', 'success')
    return redirect(url_for('main.manage_earn_actions'))

# ============== API ENDPOINTS FOR SHOPIFY ==============

@bp.route('/api/config')
def get_config():
    """API endpoint for Shopify to fetch current configuration"""
    configs = ProgramConfig.query.all()
    config_dict = {c.key: c.value for c in configs}
    
    # Get active rewards
    rewards = Reward.query.filter_by(is_active=True).order_by(Reward.display_order).all()
    rewards_list = [{
        'name': r.name,
        'points_required': r.points_required,
        'reward_value': r.reward_value,
        'reward_type': r.reward_type,
        'description': r.description
    } for r in rewards]
    
    # Get active earn actions
    actions = EarnAction.query.filter_by(is_active=True).order_by(EarnAction.display_order).all()
    actions_list = [{
        'action_key': a.action_key,
        'name': a.name,
        'points_awarded': a.points_awarded,
        'action_type': a.action_type,
        'action_url': a.action_url,
        'icon': a.icon,
        'is_repeatable': a.is_repeatable
    } for a in actions]
    
    return jsonify({
        'config': config_dict,
        'rewards': rewards_list,
        'earn_actions': actions_list
    })

@bp.route('/api/user/<email>/earned-actions')
def get_user_earned_actions(email):
    """Get which actions a user has already completed"""
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'earned': []})
    
    earned = UserEarnedAction.query.filter_by(user_id=user.user_id).all()
    earned_keys = [ea.action.action_key for ea in earned if ea.action]
    
    return jsonify({'earned': earned_keys})

@bp.route('/create-tables-temp')
def create_tables():
    try:
        db.create_all()
        return "Success! New tables created. Delete this route now."
    except Exception as e:
        return f"Error: {str(e)}"
