from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, BigInteger, Integer, String, DateTime, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, backref
from landfillpermit.data import fees, cities
from landfillpermit import db_url
import pymysql


engine = create_engine(db_url, echo=True)
Base = declarative_base()
session = Session(engine) 
########################################################################
class City(Base):
    """"""
    __tablename__ = "city"
 
    id = Column(Integer, primary_key=True)
    city_name = Column(String(40))
    users = relationship("User", backref="city")

    #----------------------------------------------------------------------
    def __init__(self, city_name):
        """"""
        self.city_name = city_name
        

class User(Base):
    """"""
    __tablename__ = "user"
 
    barcode = Column(BigInteger, primary_key=True)
    expiration_date = Column(Date)
    first_name = Column(String(40))
    last_name = Column(String(40))
    city_id = Column(Integer, ForeignKey("city.id"))
    transactions = relationship("Transactions")

    #----------------------------------------------------------------------
    def __init__(self, barcode, expiration_date, first_name, last_name, city_id):
        """"""
        self.barcode = barcode
        self.expiration_date = expiration_date
        self.first_name = first_name
        self.last_name = last_name
        self.city_id = city_id


class Fees(Base):
    """"""
    __tablename__ = "fees"
 
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    unit_of_measure = Column(String(40))
    fees_per_unit = Column(Numeric)
    fees = relationship("Transactions_Fees")

    #----------------------------------------------------------------------
    def __init__(self, name, unit_of_measure, fees_per_unit):
        """"""
        self.name = name
        self.unit_of_measure = unit_of_measure
        self.fees_per_unit = fees_per_unit


class Transactions(Base):
    """"""
    __tablename__ = "transactions"
 
    id = Column(Integer, primary_key=True)
    barcode = Column(BigInteger, ForeignKey("user.barcode"))
    transaction_timestamp = Column(DateTime)
    fees = relationship("Transactions_Fees")

    #----------------------------------------------------------------------
    def __init__(self, barcode, transaction_timestamp):
        """"""
        self.transaction_timestamp = transaction_timestamp
        self.barcode = barcode

class Transactions_Fees(Base):
    """"""
    __tablename__ = "transactions_fees"
 
    id = Column(Integer, primary_key=True)
    transactions_id = Column(Integer, ForeignKey("transactions.id"))
    fees_id = Column(Integer, ForeignKey("fees.id"))
    quantity = Column(Integer)
    
    #----------------------------------------------------------------------
    def __init__(self, transactions_id, fees_id, quantity):
        """"""
        self.transactions_id = transactions_id
        self.fees_id = fees_id
        self.quantity = quantity


# create tables
def create_db():
    Base.metadata.create_all(engine)


def populate_data():

    for key, value in fees.items():
        new_fee = Fees(key, value['unit'], value['fee'])  
        session.add(new_fee)
    session.commit()

    for city in cities:
        new_city = City(city)
        session.add(new_city)
    session.commit()