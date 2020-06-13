from flask import jsonify
from database.db import db
from models.users import UsersModel
from models.passes import PassesModel
from geopy.distance import lonlat, distance


class LocationsModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(UsersModel.id), unique=True)
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
 

    def __init__(self, user_id, longitude, latitude):
        self.user = user_id
        self.longitude = longitude
        self.latitude = latitude

  
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()

        
    @classmethod
    def ping(cls, new_lon, new_lat, user_id):
        client_location = cls.query.filter_by(user_id=user_id).first()
        client_location.longitude = new_lon
        client_location.latitude = new_lat
        db.session.commit()
        
        current_location = (new_lon, new_lat)
        users_close_to_client = []

        remaining_users = cls.query.all()
        for user in remaining_users:
            if user.user_id != user_id:
                user_location = (user.longitude, user.latitude)
                distance_between = round(distance(lonlat(*current_location), lonlat(*user_location)).meters, 1)
                if distance_between < 2000:
                    # id converted to string and has key of 'key' for react native List
                    users_close_to_client.append({
                        'key' : str(user.user_id), 
                        'username' : PassesModel.get_display_name_by_user_id(user.user_id), 
                        'distance': distance_between
                    })
        return jsonify(success=True, passes=users_close_to_client), 200
            


