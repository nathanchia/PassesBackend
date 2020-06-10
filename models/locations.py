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


    def update_location(self, new_lon, new_lat):
        self.longitude = new_lon
        self.latitude = new_lat
        db.session.commit()
        
        
    def get_other_locations(self):
        users_close_to_client = []
        
        client_location = (self.longitude, self.latitude)
        remaining_users = LocationsModel.query.all()
        for user in remaining_users:
            if user.user_id != self.user_id:
                user_location = (user.longitude, user.latitude)
                distance_between = distance(lonlat(*client_location), lonlat(*user_location)).miles
                if distance_between < 2:
                    accepted_user = UsersModel.find_user_by_id(user.user_id)
                    # id converted to string and has key of 'key' for react native List
                    users_close_to_client.append({
                        'key' : str(accepted_user.id), 
                        'username' : PassesModel.find_display_name_by_user_id(accepted_user.id), 
                        'distance': distance_between
                    })
        return users_close_to_client
            


