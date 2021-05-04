from grader.service.persistence.database import DataBaseManager
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from grader.common.models.user import User
from grader.common.models.assignment import Assignment
import json

def create_user(user: User):
    session = DataBaseManager.create_session()

    data = dict(name=user.name)
    insert = 'INSERT INTO "user" ("name") VALUES (:name)'
    session.execute(text(insert), data)
    session.commit()


def user_exists(user: User) -> bool:
    session = DataBaseManager.create_session()

    data = dict(name=user.name)
    select = 'SELECT * from "user" where name = :name'
    res = session.execute(text(select), data)
    return res.first() is not None

