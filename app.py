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

with app.app_context():
    db.create_all()


@app.route('/create',  methods=['POST'])
def create():
    content = request.json

    username = content['username']
    user_exists = UsersModel.find_user_by_username(username)
    if user_exists:
        return jsonify(msg='Username already exists'), 400

    password = content['password']
    display_name = content['displayName']

    new_user = UsersModel(username, hashlib.sha256(password.encode("utf-8")).hexdigest(), '[]')
    new_user.save_to_db()

    new_location = LocationsModel(new_user, 0.0, 0.0)
    new_location.save_to_db()

    premade = '[{"key":"InitialGreeting","title":"Greetings","text":"Hi, this is ' + display_name +'"}]'
    new_pass = PassesModel(new_user, display_name, premade)
    new_pass.save_to_db()

    return jsonify(success=True), 200
    

@app.route('/signin', methods=['POST'])
def signin():         
    content = request.json
    username = content['username']
    password = content['password']
    
    user_exists = UsersModel.find_user_by_username(username)
    if user_exists and user_exists.password == hashlib.sha256(password.encode("utf-8")).hexdigest():
        access_token = create_access_token(identity=user_exists.id)
        display_name = PassesModel.get_display_name_by_user_id(user_exists.id)
        entries = PassesModel.get_string_pass_by_user_id(user_exists.id)
        favorites = user_exists.favorites
        return jsonify(success=True, token=access_token, displayName=display_name, entries=entries, favorites=favorites), 200
    else: 
        return jsonify(msg='Invalid credentials'), 401
    

@app.route('/ping', methods=['POST'])
@jwt_required
def ping():
    identity = get_jwt_identity()
    content = request.json
    users_close_to_client = LocationsModel.ping(content['maxDistance'], content['longitude'], content['latitude'], identity)
    return jsonify(success=True, passes=users_close_to_client), 200


@app.route('/getpass', methods=['GET'])
@jwt_required
def getpass():
    user_id = request.args.get('userid')
    identity = get_jwt_identity()
    target_id = int(user_id)
    entries = PassesModel.get_string_pass_by_user_id(target_id)
    is_fav = UsersModel.is_fav(identity, target_id)
    return jsonify(success=True, entries=entries, isFav=is_fav), 200


@app.route('/changename', methods=['POST'])
@jwt_required
def changename():
    identity = get_jwt_identity()
    content = request.json
    new_name = content['newName']
    PassesModel.update_display_name(identity, new_name)
    return jsonify(success=True), 200


@app.route('/updateentries', methods=['POST'])
@jwt_required
def updateentries():
    identity = get_jwt_identity()
    content = request.json
    new_entries = content['newEntries']
    PassesModel.update_entries(identity, new_entries)
    return jsonify(success=True), 200


@app.route('/updatefav', methods=['POST'])
@jwt_required
def updatefav():
    identity = get_jwt_identity()
    content = request.json
    new_favorites = content['newFav']
    UsersModel.update_favorites(identity, new_favorites)
    return jsonify(success=True), 200


if __name__ == '__main__':
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