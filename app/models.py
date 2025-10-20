from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Pokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(30))
    level = db.Column(db.Integer, default=1)
