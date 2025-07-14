from flask import Blueprint, render_template, request, redirect, url_for
from .models import User
from . import db

bp = Blueprint('main', __name__)

@bp.route('/')
def health():
    return "OK", 200

@bp.route('/users')
def list_users():
    q       = request.args.get('q', '')
    page    = request.args.get('page', 1, type=int)
    per_page = 300

    # build base query
    query = User.query
    if q:
        query = query.filter(
            (User.first_name.ilike(f'%{q}%')) |
            (User.email.ilike(f'%{q}%'))
        )

    # paginate: returns a Pagination object
    pagination = query.order_by(User.user_id) \
                      .paginate(page=page, per_page=per_page, error_out=False)

    users = pagination.items

    return render_template(
        'users.html',
        users=pagination.items,
        q=q,
        pagination=pagination
    )



@bp.route('/users/<int:user_id>/points', methods=['POST'])
def update_points(user_id):
    amount = int(request.form.get('amount', 0))
    user   = User.query.get_or_404(user_id)
    user.points = max(0, user.points + amount)
    db.session.commit()
    return redirect(url_for('main.list_users', page=request.args.get('page', 1, type=int), q=request.args.get('q', '')))

