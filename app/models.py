from . import db

class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    user_id                    = Column(Integer, primary_key=True)
    shopify_customer_id        = Column(String(255), nullable=True)
    first_name                 = Column(String(255), nullable=True)
    last_name                  = Column(String(255), nullable=True)
    email                      = Column(String(255), unique=True, nullable=False)
    date_of_birth              = Column(Date, nullable=True)
    membership_status          = Column(String(50), nullable=True)
    vip_tier_name              = Column(String(100), nullable=True)
    points                     = Column(Integer, default=0, nullable=False)
    referral_count             = Column(Integer, default=0, nullable=False)
    referral_purchases_count   = Column(Integer, default=0, nullable=False)
    referral_code              = Column(String(50), unique=True, nullable=True)
    referral_discount_code     = Column(Text, nullable=True)
    discount_code_id           = Column(Integer, nullable=True)
    referred_by                = Column(String(50), nullable=True)
    last_discount_code         = Column(String(50), nullable=True)
    created_at                 = Column(DateTime, server_default=func.now())
