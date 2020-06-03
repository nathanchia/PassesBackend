from database.db import db


class PassesModel(db.Model):
    __tablename__ = "passes"
    id = db.Column(db.Integer, primary_key=True)
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
