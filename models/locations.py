from database.db import db
from models.users import UsersModel
from geopy.distance import lonlat, distance


class LocationsModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(UsersModel.id), unique=True)
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
 

    def __init__(self, longitude, latitude, user_id):
        self.longitude = longitude
        self.latitude = latitude
        self.user = user_id

  
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def update_location(self, new_lon, new_lat):
        self.longitude = new_lon
        self.latitude = new_lat
        db.session.commit()
        

    @classmethod
    def find_user_by_userid(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()

    @classmethod
    def get_other_locations_within(cls, user_id):
        client = cls.query.filter_by(user_id=user_id).first()
        client_location = (client.longitude, client.latitude)
        users_close_to_client = []
        remaining_users = cls.query.all()
        for user in remaining_users:
            user_location = (user.longitude, user.latitude)
            distance_between = distance(lonlat(*client_location), lonlat(*user_location)).miles
            if distance_between < 2:
                accepted_user = UsersModel.find_user_by_id(user.user_id)
                # id converted to string and has key of 'key' for react native List
                users_close_to_client.append({'key' : str(accepted_user.id), 'username' : accepted_user.username,'distance': distance_between})
        return users_close_to_client

            


