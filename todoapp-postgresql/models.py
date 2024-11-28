from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

"""
{
  "username": "parvin",
  "email": "parvin@email.com",
  "first_name": "parvin",
  "last_name": "parvin",
  "password": "test1234",
  "role": "admin"
},
{
  "username": "example1",
  "email": "example@email.com",
  "first_name": "example",
  "last_name": "user",
  "password": "test1234",
  "role": ""
}
"""

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)


class Todos(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))