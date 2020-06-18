from database.db import db
import json

class UsersModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(), nullable=False)
    location = db.relationship('LocationsModel', backref='user', uselist=False)
    passInfo = db.relationship('PassesModel', backref='user', uselist=False)
    favorites = db.Column(db.Text, nullable=False)
    

    def __init__(self, username, password, favorites):
        self.username = username
        self.password = password
        self.favorites = favorites
  
  
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


    @classmethod
    def update_favorites(cls, _id, new_fav):
        user = cls.query.filter_by(id=_id).first()
        user.favorites = new_fav
        db.session.commit()


    # Checks whether the user_id has favorited target_id
    # If so, returns true, else false
    @classmethod
    def is_fav(cls, user_id, target_id):
        user = cls.query.filter_by(id=user_id).first()
        is_fav = False
        fav_list = json.loads(user.favorites)
        for fav in fav_list:
            if (int(fav["key"]) == target_id):
                is_fav = True
        return is_fav