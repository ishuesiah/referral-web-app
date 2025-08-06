import os
import time
import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, session
from functools import wraps
from .models import User
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
    page = request.args.get('page', 1, type=int)
    per_page = 300

    query = User.query
    if q:
        query = query.filter(or_(
            User.first_name.ilike(f'%{q}%'),
            User.email.ilike(f'%{q}%'),
            User.referral_code.ilike(f'%{q}%'),
            # cast the JSON column to text so you can search inside it:
            cast(User.referral_discount_code, Text).ilike(f'%{q}%')
        ))

    pagination = query.order_by(User.user_id) \
                      .paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        'users.html', users=pagination.items, q=q, pagination=pagination
    )

@bp.route('/users/<int:user_id>/points', methods=['POST'])
@login_required
def update_points(user_id):
    amount = int(request.form.get('amount', 0))
    user = User.query.get_or_404(user_id)
    user.points = max(0, user.points + amount)
    db.session.commit()
    return redirect(url_for('main.list_users', page=request.args.get('page', 1), q=request.args.get('q', '')))
