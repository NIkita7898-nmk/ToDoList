from flask import request, jsonify
from flask import Blueprint
from passlib.hash import pbkdf2_sha256
import jwt
from functools import wraps
from flask import request

from models import User, Task
from db import db

from datetime import datetime

# Create a blueprint
bp = Blueprint("views", __name__)
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
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
        return jsonify({"message": "Email is already exist"}), 409
    elif len(data["phone_number"]) != 10:
        return jsonify({"message": "Phone Number length should be 10"}), 400
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
        return jsonify({"message": "Account Created Successfully"}), 201
                     
                                                                                                               
def verify_password(provided_password, stored_password):
    return pbkdf2_sha256.verify(provided_password, stored_password)


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
    else:
        stored_password = User.query.filter_by(email=data["email"]).first().password
        provided_password = data["password"]
        if verify_password(provided_password, stored_password):
            access_token = create_access_token(identity=data["email"])
            refresh_token = create_refresh_token(identity=data["email"])
            return jsonify(access_token=access_token, refresh_token=refresh_token), 201
        else:
            return jsonify({"message": "Incorrect Password"}), 401


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
            data = jwt.decode(token, "super-secret", algorithms=["HS256"])
            decoded_token = decode_token(token)
            user_email = decoded_token["sub"]
            current_user = User.query.filter_by(email=user_email).first().id
            if current_user is None:
                return {
                    "message": "Invalid Authentication token!",
                    "data": None,
                    "error": "Unauthorized",
                }, 401
        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e),
            }, 500

        return f(current_user, *args, **kwargs)

    return decorated


@bp.route("/get-user/", methods=["GET"])
def get_user():
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
    user = User.query.filter_by(id=current_user).first()

    if user:
        user_dict = {
            "id": user.id,
            "name": f"{user.firstname} {user.lastname}",
            "email": user.email,
            "address": user.address,
            "phone_no": str(user.phone_number),
        }
        return jsonify({"user": user_dict}), 200
    else:
        return jsonify({"message": "User not found"}), 404


# @bp.route("/add-task/", methods=["POST"])
@token_required
def add_task(current_user):
    data = request.json
    if "task_title" not in data.keys():
        return jsonify({"message": "task_title is missing"}), 400
    else:
        task_title = request.json["task_title"]
        description = (
            request.json["description"]
            if "description" in request.json.keys()
            else None
        )
        status = request.json["status"] if "status" in request.json.keys() else None
        started_on = datetime.now().date()
        user_id = current_user
        task_data = Task(
            user_id=user_id,
            task_title=task_title,
            description=description,
            status=status,
            started_on=started_on,
        )
        db.session.add(task_data)
        db.session.commit()
        response_data = {
            "id": task_data.id,
            "user_id": task_data.user_id,
            "task_title": task_data.task_title,
            "description": task_data.description,
            "status": task_data.status.value if task_data.status else None,
            "started_on": str(task_data.started_on),
            "completed_on": None,
        }
        return jsonify({"data": response_data}), 201


@bp.route("/update-task/<int:id>/", methods=["PATCH"])
@token_required
def update_task(current_user, id):
    data = request.json
    task = Task.query.filter_by(id=id, user_id=current_user).first()
    if task:
        task.task_title = (
            data["task_title"] if "task_title" in data.keys() else task.task_title
        )
        task.status = data["status"] if "status" in data.keys() else task.status
        if task.status == "Done" and "status" in data.keys():
            task.completed_on = datetime.now().date()

        task.description = (
            data["description"] if "description" in data.keys() else task.description
        )
        db.session.commit()
        response_data = {
            "id": task.id,
            "user_id": task.user_id,
            "task_title": task.task_title,
            "description": task.description,
            "status": task.status.value,
            "started_on": task.started_on,
            "completed_on": task.completed_on,
        }
        return jsonify({"data": response_data}), 200
    else:
        return jsonify({"message": "Task not found"}), 404


@bp.route("/delete-task/<int:id>/", methods=["Delete"])
@token_required
def delete_task(current_user, id):
    task = Task.query.filter_by(id=id, user_id=current_user).first()
    if task:
        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": "Task deleted successfully"}), 200
    else:
        return jsonify({"message": "Task not found"}), 404



