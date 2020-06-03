from flask import Flask, jsonify, request
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token, get_jwt_identity)
from database.db import db
from models.users import UsersModel
import hashlib


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['JWT_SECRET_KEY'] = 'd0nt h4ck m3 pl5'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

jwt = JWTManager(app)


@app.route('/create',  methods=['POST'])
def create():
    # Parameter check
    if not request.is_json: 
        return jsonify(msg='Missing JSON request'), 400
        
    content = request.json

    username = content['username']
    if not username:
        return jsonify(msg='Missing username parameter'), 400
    user_exists = UsersModel.find_user_by_username(username)

    password = content['password']
    if not password:
        return jsonify(msg='Missing password parameter'), 400

    # Creating new account
    if request.method == 'POST':
        # display_name = content['displayName']
        # if not display_name:
        #     return jsonify(msg='Missing display name parameter'), 400

        if user_exists:
            return jsonify(msg='Username already exists'), 400
        
        # Registering new user to database
        new_user = UsersModel(username, hashlib.sha256(password.encode("utf-8")).hexdigest())
        new_user.save_to_db()

        return jsonify(msg='Successfully created new user'), 200
    else:
        return jsonify(msg='Wrong request methods')

@app.route('/signin', methods=['POST'])
def signin():   
    # Parameter check
    if not request.is_json: 
        return jsonify(msg='Missing JSON request'), 400
        
    content = request.json

    username = content['username']
    if not username:
        return jsonify(msg='Missing username parameter'), 400
    user_exists = UsersModel.find_user_by_username(username)

    password = content['password']
    if not password:
        return jsonify(msg='Missing password parameter'), 400

    if request.method == 'POST':  
        if user_exists and user_exists.password == hashlib.sha256(password.encode("utf-8")).hexdigest():
            access_token = create_access_token(identity=user_exists.id)
            return jsonify(token= access_token), 200
        else: 
            return jsonify(msg='Wrong credentials'), 401
    else:
        return jsonify(msg='Wrong request methods')


@app.route('/ping', methods=['POST'])
@jwt_required
def ping():
    if request.method == 'POST':
        current_user = get_jwt_identity()
        content = request.json
        print ('longitude: ' + str(content['longitude']) + ', latitude: ' + str(content['latitude']))
        msg = 'It was a success, ' + UsersModel.query.get(current_user).username
        return jsonify(msg=msg)
    else:
        return jsonify(msg='Wrong request methods')


if __name__ == '__main__':
    @app.before_first_request
    def create_tables():
        db.create_all()

    app.run()
