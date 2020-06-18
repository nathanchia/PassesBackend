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
    def ping(cls, max_distance, new_lon, new_lat, user_id):
        client_location = cls.query.filter_by(user_id=user_id).first()
        client_location.longitude = new_lon
        client_location.latitude = new_lat
        db.session.commit()
        
        current_location = (new_lon, new_lat)
        users_close_to_client = []
        max_valid = 15 # Arbitrary number
        
        remaining_users = cls.query.all()
        for user in remaining_users:
            # Make sure user is not returned himself
            if user.user_id != user_id:
                # Get distance
                user_location = (user.longitude, user.latitude)
                distance_between = round(distance(lonlat(*current_location), lonlat(*user_location)).miles, 1)
                if max_distance == 'none' or distance_between <= int(max_distance):
                    # Just append since not max yet
                    if max_valid > 0:
                        max_valid -= 1
                        
                        # Populate empty list
                        if len(users_close_to_client) == 0:
                            users_close_to_client.append({
                                'key' : str(user.user_id), 
                                'displayName' : PassesModel.get_display_name_by_user_id(user.user_id), 
                                'distance': distance_between
                            })
                        
                        # Find the correct index to insert pass otherwise
                        else:
                            for i in range(len(users_close_to_client)):
                                if users_close_to_client[i]['distance'] > distance_between:
                                    users_close_to_client.insert(i, {
                                        'key' : str(user.user_id), 
                                        'displayName' : PassesModel.get_display_name_by_user_id(user.user_id), 
                                        'distance': distance_between
                                    })
                                    break
                                # Since will add this entry either way, if largest distance, append to end
                                if i == len(users_close_to_client) - 1:
                                    users_close_to_client.append({
                                        'key' : str(user.user_id), 
                                        'displayName' : PassesModel.get_display_name_by_user_id(user.user_id), 
                                        'distance': distance_between
                                    })
                    else:
                        # Max number of passes allowed
                        # Checks through all the entries in the list. If find a suitable slot,
                        # insert, and delete last (largest distance) entry
                        for i in range(len(users_close_to_client)):
                            if users_close_to_client[i]['distance'] > distance_between:
                                users_close_to_client.insert(i, {
                                    'key' : str(user.user_id), 
                                    'displayName' : PassesModel.get_display_name_by_user_id(user.user_id), 
                                    'distance': distance_between
                                })
                                del users_close_to_client[-1]
                                break

        return users_close_to_client
        
            


