from flask import Blueprint, render_template, request, redirect, url_for
from .models import User
from . import db

bp = Blueprint('main', __name__)

@bp.route('/users')
def list_users():
    q = request.args.get('q', '')
    if q:
        users = User.query.filter(
            (User.first_name.ilike(f'%{q}%')) |
            (User.email.ilike(f'%{q}%'))
        ).all()
    else:
        users = User.query.all()
    return render_template('users.html', users=users, q=q)

@bp.route('/users/<int:user_id>/points', methods=['POST'])
def update_points(user_id):
    action = request.form.get('action')  # "add" or "subtract"
    amount = int(request.form.get('amount', 1))
    user = User.query.get_or_404(user_id)
    if action == 'add':
        user.points += amount
    else:
        user.points = max(0, user.points - amount)
    db.session.commit()
    return redirect(url_for('main.list_users'))
