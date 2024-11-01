from typing import Annotated
from sqlalchemy.orm import Session

from fastapi import FastAPI, Depends
import models
from models import Todos
from database import engine, SessionLocal



app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# yield means only the code prior to and including the yield statement is executed before sending a response
# the code following the yield statement is executed after the response has been delivered.
# this makes fastapi quicker, because we can fetch info from a db, return it to the client and then close off the
# connection after and it's extremely safe and pretty much required in most applications to open up a database
# connection only for when you're using a database and then close the connection after.

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/")
async def read_all(db: db_dependency):
    return db.query(Todos).all()