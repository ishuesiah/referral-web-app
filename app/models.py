from . import db

class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    user_id              = db.Column(db.Integer, primary_key=True)
    shopify_customer_id  = db.Column(db.String(255), nullable=True)
    first_name           = db.Column(db.String(255), nullable=True)
    email                = db.Column(db.String(255), unique=True, nullable=False)
    points               = db.Column(db.Integer, default=0)
    referral_code        = db.Column(db.String(50), unique=True, nullable=True)
    referred_by          = db.Column(db.String(50), nullable=True)
    last_discount_code   = db.Column(db.String(50), nullable=True)
    created_at           = db.Column(db.DateTime, server_default=db.func.now())
