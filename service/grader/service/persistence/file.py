from grader.service.persistence.database import DataBaseManager
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from grader.common.models.user import User
import json

def get_files_of_assignment(user: User, assignid: int):
    engine = create_engine(DataBaseManager.get_database_url(), echo=True)
    session = Session(bind=engine)
    select = "SELECT * FROM file WHERE assignid=%i" % assignid
    res = session.execute(select)
    res = json.dumps([dict(x) for x in res])
    session.commit()
    return res

def get_exercises_of_assignment(user: User, assignid: int):
    engine = create_engine('sqlite:///grader.db', echo=True)
    session = Session(bind=engine)
    select = "SELECT * FROM file WHERE assignid=%i AND exercise=true" % assignid
    res = session.execute(select)
    res = json.dumps([dict(x) for x in res])
    session.commit()
    return res
