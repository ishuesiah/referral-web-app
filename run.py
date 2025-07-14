from app import create_app, db
from app.models import User  # import your model so it’s registered with SQLAlchemy

app = create_app()

# CLI command to create all tables (runs once)
@app.cli.command('init-db')
def init_db():
    db.create_all()
    print('Database initialized.')

if __name__ == '__main__':
    app.run(debug=True)
