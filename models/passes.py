from database.db import db
from models.users import UsersModel


class PassesModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(UsersModel.id), unique=True)
    display_name = db.Column(db.String(80), nullable=False)
    

    def __init__(self, user_id, display_name):
        self.user = user_id
        self.display_name = display_name

  
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def find_display_name_by_user_id(cls, user_id):
        target_pass = cls.query.filter_by(user_id=user_id).first()
        return target_pass.display_name

    

        

  
