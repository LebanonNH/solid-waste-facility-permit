import os
from sqlalchemy import create_engine, ForeignKey, Column, Date, String, Integer, DateTime, Numeric
from sqlalchemy.orm import Session, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv('DB_PATH'))

Base = declarative_base()
class City(Base):
    """"""
    __tablename__ = "city"
 
    id = Column(Integer, primary_key=True)
    city_name = Column(String)

    #----------------------------------------------------------------------
    def __init__(self, city_name):
        """"""
        self.city_name = city_name

class User(Base):
    """"""
    __tablename__ = "user"
 
    barcode = Column(Integer, primary_key=True)
    expiration_date = Column(Date)
    first_name = Column(String)
    last_name = Column(String)
    city_id = Column(String, ForeignKey("city.id"))

    #----------------------------------------------------------------------
    def __init__(self, barcode, expiration_date, first_name, last_name, city_id):
        """"""
        self.barcode = barcode
        self.expiration_date = expiration_date
        self.first_name = first_name
        self.last_name = last_name
        self.city_id = city_id

session = Session(engine)