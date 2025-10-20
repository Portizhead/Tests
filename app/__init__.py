from flask import Flask
from .models import db
from .main.routes import main_bp
from .auth.routes import auth_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'cámbialo-luego'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pokedex.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # crea tablas si no existen
    with app.app_context():
        db.create_all()

    return app

app = create_app()
