import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime, Boolean, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from flask_login import UserMixin


Base = declarative_base()


# User entity defined here
# Each column is called attribute
class Users(Base, UserMixin):
    __tablename__ = 'Users'

    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    FullName = Column(String(30), nullable=False)
    PhoneNumber = Column(String(15), nullable=False, unique=True)
    UserType = Column(String(10), nullable=False,)
    EmailAddress = Column(String(40), nullable=False, unique=True)
    Password = Column(String(255), nullable=False)
    CreatedDate = Column(DateTime, default=datetime.datetime.utcnow)

    def get_id(self):
        return self.ID

# Product entity 
class Product(Base):
    __tablename__ = 'products'

    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    ProductName = Column(String(100), nullable=False, unique=True)
    ProductDescription = Column(String(300), nullable=False)
    Price = Column(Integer, nullable=False)
    Category = Column(String(20), nullable=False)
    Landlord = Column(Integer, ForeignKey(Users.ID))
    Users = relationship(Users)
    Date = Column(DateTime, default=datetime.datetime.utcnow)


# Order entity 
class Reserve(Base):
    __tablename__ = 'reserves'

    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    ProductName = Column(String(100), nullable=False, unique=False)
    ReceiverName = Column(String(100), nullable=False, unique=False)
    PhoneNumber = Column(String(15), nullable=False, unique=False)
    Address = Column(String(300), nullable=False)
    Date = Column(DateTime, default=datetime.datetime.utcnow)


# Categories Entity
class Category(Base):
    __tablename__ = 'categories'

    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    Name = Column(String(100), nullable=False, unique=True)


# Always stay at the end of the file
engine = create_engine('sqlite:///HRMS.db')
Base.metadata.create_all(engine)
