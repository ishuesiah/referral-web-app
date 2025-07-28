from . import db

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
    referral_discount_code     = db.Column(db.Text, nullable=True)
    discount_code_id           = db.Column(db.Integer, nullable=True)

    referred_by                = db.Column(db.String(50), nullable=True)
    last_discount_code         = db.Column(db.String(50), nullable=True)

    created_at                 = db.Column(
                                   db.DateTime,
                                   server_default=db.func.now(),
                                   nullable=False
                                 )
