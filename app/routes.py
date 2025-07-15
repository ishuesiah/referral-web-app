import os
from flask import Blueprint, render_template, request, redirect, url_for, session
from functools import wraps
from werkzeug.security import check_password_hash
from .models import User
from . import db

bp = Blueprint('main', __name__)

@bp.route('/health')
def health():
    return "OK", 200

@bp.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        pwd = request.form.get('password', '')
        pwd_hash = os.getenv('ADMIN_PASSWORD_HASH', '')
        if pwd_hash and check_password_hash(pwd_hash, pwd):
            session['logged_in'] = True
            return redirect(url_for('main.list_users'))
        error = 'Invalid password'
    return render_template('login.html', error=error)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('main.login'))
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
        query = query.filter(
            (User.first_name.ilike(f'%{q}%')) |
            (User.email.ilike(f'%{q}%'))
        )

    pagination = query.order_by(User.user_id) \
                      .paginate(page=page, per_page=per_page, error_out=False)

    return render_template('users.html', users=pagination.items, q=q, pagination=pagination)

@bp.route('/users/<int:user_id>/points', methods=['POST'])
@login_required
def update_points(user_id):
    amount = int(request.form.get('amount', 0))
    user = User.query.get_or_404(user_id)
    user.points = max(0, user.points + amount)
    db.session.commit()
    return redirect(url_for('main.list_users', page=request.args.get('page', 1), q=request.args.get('q', '')))
