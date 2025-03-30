from flask import Flask
from backend.models import *

app = None

def setup_app():
    
    app = Flask(__name__)

    #coniguration of database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
    app.config['SECRET_KEY'] = 'mysecretkey'  

    db.init_app(app) 
    app.app_context().push()
    app.debug = True

setup_app()

from backend.controllers import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash='admin123',  
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()

    app.run()