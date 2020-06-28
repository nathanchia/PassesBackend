from flask import Flask, jsonify, request, render_template
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token, get_jwt_identity)
from threading import Thread
from flask_mail import Mail, Message
import hashlib
import datetime

from database.db import db
from models.users import UsersModel
from models.locations import LocationsModel
from models.passes import PassesModel


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['JWT_SECRET_KEY'] = 'd0nt h4ck m3 pl5'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'clocards.service@gmail.com',
    "MAIL_PASSWORD": 'tmlrblzcqmleiumi'
}
app.config.update(mail_settings)

mail = Mail(app)

jwt = JWTManager(app)

db.init_app(app)
with app.app_context():
    db.create_all()


@app.route('/create',  methods=['POST'])
def create():
    content = request.json

    username = content['username']
    user_exists = UsersModel.find_user_by_username(username)
    if user_exists:
        return jsonify(success=False, msg='Username already exists'), 409

    email = content['email']
    email_exists = UsersModel.find_user_by_email(email)
    if email_exists:
        return jsonify(success=False, msg='Email already used'), 409

    password = content['password']
    display_name = content['displayName']

    new_user = UsersModel(username, hashlib.sha256(password.encode("utf-8")).hexdigest(), email)
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
        return jsonify(success=False, msg='Invalid credentials'), 401


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


@app.route('/changepass', methods=['POST'])
@jwt_required
def changepass():
    identity = get_jwt_identity()
    content = request.json
    old_password = content['oldPassword']
    new_password = content['newPassword']
    user = UsersModel.find_user_by_id(identity)
    if user.password != hashlib.sha256(old_password.encode("utf-8")).hexdigest():
        return jsonify(success=False, msg='Invalid password'), 401
    else:
        user.password = hashlib.sha256(new_password.encode("utf-8")).hexdigest()
        db.session.commit()
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


# Recover Password Email
def send_email(app, msg):
    with app.app_context():
        mail.send(msg)


@app.route('/forgot', methods=['POST'])
def fogot():
    content = request.json
    email = content['email']
    email_exists = UsersModel.find_user_by_email(email)
    if email_exists:
        expires = datetime.timedelta(minutes=5)
        access_token = create_access_token(identity=email_exists.id, expires_delta=expires)
        link = 'https://nkchia.pythonanywhere.com/recover?t=' + access_token 
        msg = Message (
            subject="CloCards Password Recovery",
            sender=app.config.get("MAIL_USERNAME"),
            recipients=[email],
            body="Follow this link to reset your Clocards account password:\n" + link
        )
        Thread(target=send_email, args=(app, msg)).start()
        return jsonify(success=True), 200
    else: 
        return jsonify(success=False, msg='Email does not exist'), 404


@app.route('/recover', methods=['GET'])
def recover():
    return render_template('recover.html')


@app.route('/reset', methods=['POST'])
@jwt_required
def result():
    identity = get_jwt_identity()
    content = request.json
    new_password = content['newPassword']
    user = UsersModel.find_user_by_id(identity)
    user.password = hashlib.sha256(new_password.encode("utf-8")).hexdigest()
    db.session.commit()
    return jsonify(success=True), 200


@app.route('/expire', methods=['GET'])
def expired():
    return render_template('expire.html')


@app.route('/success', methods=['GET'])
def success():
    return render_template('success.html')


if __name__ == '__main__':
    app.run()