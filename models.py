from sqlalchemy.sql import func
from enum import Enum
from db import db
import os
from flask_sqlalchemy import SQLAlchemy


class TaskStatus(Enum):
    ToDo = "To Do"
    InProgress = "In Progress"
    Done = "Done"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(40), nullable=False)
    lastname = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.Integer, nullable=True)
    address = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    task = db.relationship("Task", backref="user", cascade="all, delete, delete-orphan")
    __table_args__ = (
        db.CheckConstraint("LENGTH(phone_number) = 10", name="check_integer_length"),
    )

    # def __repr__(self):
    #     return f"{self.firstname} {self.lastname}"


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    task_title = db.Column(db.String(40), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    status = db.Column(db.Enum(TaskStatus))
    started_on = db.Column(db.Date)
    completed_on = db.Column(db.Date)

    def __repr__(self):
        return f"{self.task_title}"
