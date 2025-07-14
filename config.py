import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # your JSON‐style MySQL credentials
    MYSQL_CONFIG = {
        'host':     'northamerica-northeast1-001.proxy.kinsta.app',
        'port':     30387,
        'user':     'hemlockandoak',
        'password': 'jH3&wM0gH2a',
        'database': 'referral_program_db'
    }

    # build the URI for SQLAlchemy
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://"
        f"{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}@"
        f"{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/"
        f"{MYSQL_CONFIG['database']}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # keep your Flask secret in the environment
    SECRET_KEY = os.getenv('SECRET_KEY', 'you-should-override-this')
