import os
from app import create_app

app = create_app()

@app.cli.command('init-db')
def init_db():
    from app import db
    db.create_all()
    print('Database initialized.')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
