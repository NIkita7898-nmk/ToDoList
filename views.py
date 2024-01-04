from flask import request, jsonify
from flask.views import MethodView
from flask import Blueprint
from passlib.hash import pbkdf2_sha256
import jwt
from functools import wraps
from flask import request, abort

from models import User
from db import db
from flask import current_app

# Create a blueprint
bp = Blueprint("views", __name__)
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    decode_token,
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


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split("Bearer ")[1]
        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized",
            }, 401
        try:
            print("in try block")
            data = jwt.decode(token, "super-secret", algorithms=["HS256"])

            current_user = User().get_by_id(data["user_id"])
            if current_user is None:
                return {
                    "message": "Invalid Authentication token!",
                    "data": None,
                    "error": "Unauthorized",
                }, 401
            if not current_user["active"]:
                abort(403)
        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e),
            }, 500

        return f(current_user, *args, **kwargs)

    return decorated


@bp.route("/get-user/", methods=["GET"])
def get_user(current_user):
    users = User.query.all()
    all_user = []
    for user in users:
        user_dict = {
            "id": user.id,
            "name": f"{user.firstname} {user.lastname}",
            "email": user.email,
            "address": user.address,
            "phone_no": str(user.phone_number),
        }
        all_user.append(user_dict)
    return jsonify({"users": all_user})


@bp.route("/get-current-user/", methods=["GET"])
@token_required
def get_current_user(current_user):
    users = User.query.all()
    all_user = []
    for user in users:
        user_dict = {
            "id": user.id,
            "name": f"{user.firstname} {user.lastname}",
            "email": user.email,
            "address": user.address,
            "phone_no": str(user.phone_number),
        }
        all_user.append(user_dict)
    return jsonify({"users": all_user})
