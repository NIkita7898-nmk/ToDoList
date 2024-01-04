from flask import request, jsonify
from flask.views import MethodView
from flask import Blueprint
from passlib.hash import pbkdf2_sha256

from models import User
from db import db

# Create a blueprint
bp = Blueprint("views", __name__)
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)


@bp.route("/")
def home():
    return "home"


@bp.route("/registration/", methods=["POST"])
def registration():
    expected_keys = ["firstname", "lastname", "email", "password"]
    data = request.json
    email = User.query.filter_by(email=data["email"]).first()
    missing_keys = set(expected_keys) - set(request.json.keys())
    if missing_keys:
        return (
            jsonify({"message": f"some fields are missing: {', '.join(missing_keys)}"}),
            400,
        )
    elif email is not None:
        return "Email is already exist"
    elif len(data["phone_number"]) != 10:
        return "Phone Number length should be 10"
    else:
        data["password"] = pbkdf2_sha256.hash(data["password"])
        user_data = User(
            firstname=data["firstname"],
            lastname=data["lastname"],
            email=data["email"],
            password=data["password"],
            address=data["address"],
            phone_number=data["phone_number"],
        )
        db.session.add(user_data)
        db.session.commit()
        return "Account Created Successfully"


@bp.route("/login/", methods=["POST"])
def login():
    expected_keys = ["email", "password"]
    missing_keys = set(expected_keys) - set(request.json.keys())
    data = request.json
    if missing_keys:
        return (
            jsonify({"message": f"Please Enter:  {' and '.join(missing_keys)}"}),
            400,
        )

    elif User.query.filter_by(email=data["email"]).first() is None:
        return (
            jsonify({"message": "This email is not registered"}),
            400,
        )
    elif (
        User.query.filter_by(email=data["email"], password=data["password"]).first()
        is None
    ):
        return (
            jsonify({"message": "Incorrect password"}),
            400,
        )
    else:
        access_token = create_access_token(identity=data["email"])
        refresh_token = create_refresh_token(identity=data["email"])
        return jsonify(access_token=access_token, refresh_token=refresh_token), 201
