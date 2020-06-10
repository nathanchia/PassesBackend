from flask import Flask, jsonify, request
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token, get_jwt_identity)
from database.db import db
from models.users import UsersModel
from models.locations import LocationsModel
from models.passes import PassesModel
import hashlib


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['JWT_SECRET_KEY'] = 'd0nt h4ck m3 pl5'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

jwt = JWTManager(app)


@app.route('/create',  methods=['POST'])
def create():
    content = request.json

    username = content['username']
    user_exists = UsersModel.find_user_by_username(username)
    if user_exists:
        return jsonify(msg='Username already exists'), 400

    password = content['password']
    display_name = content['displayName']

    new_user = UsersModel(username, hashlib.sha256(password.encode("utf-8")).hexdigest())
    new_user.save_to_db()

    new_location = LocationsModel(new_user, 0.0, 0.0)
    new_location.save_to_db()

    new_pass = PassesModel(new_user, display_name)
    new_pass.save_to_db()

    return jsonify(msg='Successfully created new user'), 200
    

@app.route('/signin', methods=['POST'])
def signin():         
    content = request.json
    username = content['username']
    password = content['password']
    
    user_exists = UsersModel.find_user_by_username(username)
    if user_exists and user_exists.password == hashlib.sha256(password.encode("utf-8")).hexdigest():
        access_token = create_access_token(identity=user_exists.id)
        display_name = PassesModel.find_display_name_by_user_id(user_exists.id)
        return jsonify(token=access_token, displayName=display_name), 200
    else: 
        return jsonify(msg='Invalid credentials'), 401
    

@app.route('/ping', methods=['POST'])
@jwt_required
def ping():
    identity = get_jwt_identity()
    content = request.json
    client_location = LocationsModel.query.filter_by(user_id=identity).first()
    client_location.update_location(content['longitude'], content['latitude'])
    users_close_to_client = client_location.get_other_locations()
    return jsonify(msg = users_close_to_client), 200


@app.route('/passdisplay', methods=['GET'])
@jwt_required
def passdisplay():
    pass


if __name__ == '__main__':
    @app.before_first_request
    def create_tables():
        db.create_all()

    app.run()


# Parameter check
#    if not request.is_json: 
#        return jsonify(msg='Missing JSON request'), 400
        
#    content = request.json

#    username = content['username']
#    if not username:
#        return jsonify(msg='Missing username parameter'), 400

#    password = content['password']
#    if not password:
#        return jsonify(msg='Missing password parameter'), 400

#    display_name = content['displayName']
#    if not display_name:
#       return jsonify(msg='Missing display name parameter'), 400