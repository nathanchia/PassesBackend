from database.db import db


class UsersModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(), nullable=False)
    location = db.relationship('LocationsModel', backref='user', uselist=False)


    def __init__(self, username, password):
        self.username = username
        self.password = password

  
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()


    @classmethod
    def find_user_by_username(cls, username):
        return cls.query.filter_by(username=username).first()


    @classmethod
    def find_user_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()


