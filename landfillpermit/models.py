from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, BigInteger, Integer, String, DateTime, Numeric, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, backref
from landfillpermit.data import fees, cities
from landfillpermit import db_url, root_user, root_password
import pymysql


engine = create_engine(db_url, echo=True)
Base = declarative_base()
session = Session(engine) 
########################################################################
class City(Base):
    """"""
    __tablename__ = "city"
 
    id = Column(Integer, primary_key=True)
    city_name = Column(String(40), nullable=False)
    users = relationship("User", backref="city")

    #----------------------------------------------------------------------
    def __init__(self, city_name):
        """"""
        self.city_name = city_name
        

class User(Base):
    """"""
    __tablename__ = "user"
 
    barcode = Column(BigInteger, primary_key=True)
    expiration_date = Column(Date, nullable=False)
    first_name = Column(String(40), nullable=False)
    last_name = Column(String(40), nullable=False)
    city_id = Column(Integer, ForeignKey("city.id"), nullable=False)
    email = Column(String(80), nullable=False)
    transactions = relationship("Transactions")

    #----------------------------------------------------------------------
    def __init__(self, barcode, expiration_date, first_name, last_name, city_id, email):
        """"""
        self.barcode = barcode
        self.expiration_date = expiration_date
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.city_id = city_id


class Fees(Base):
    """"""
    __tablename__ = "fees"
 
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    weight = Column(Numeric, default=200, nullable=False)
    unit_of_measure = Column(String(40))
    fees_per_unit = Column(Numeric(precision=10, scale=2), nullable=False)
    fees = relationship("Transactions_Fees")

    #----------------------------------------------------------------------
    def __init__(self, name, fees_per_unit, unit_of_measure="", weight=200):
        """"""
        self.name = name
        self.fees_per_unit = fees_per_unit
        self.unit_of_measure = unit_of_measure
        self.weight=weight


class Transactions(Base):
    """"""
    __tablename__ = "transactions"
 
    id = Column(Integer, primary_key=True)
    barcode = Column(BigInteger, ForeignKey("user.barcode"), nullable=False)
    transaction_timestamp = Column(DateTime, nullable=False)
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
    transactions_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    fees_id = Column(Integer, ForeignKey("fees.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    
    #----------------------------------------------------------------------
    def __init__(self, transactions_id, fees_id, quantity):
        """"""
        self.transactions_id = transactions_id
        self.fees_id = fees_id
        self.quantity = quantity

class Employee(Base):
    """"""
    __tablename__ = "employees"
 
    id = Column(Integer, primary_key=True)
    username = Column(String(120), unique=True, nullable=False)
    password = Column(String(60), nullable=False)
    is_admin = Column(Boolean, default=False)
    
    #----------------------------------------------------------------------
    def __init__(self, username, password, is_admin=False):
        """"""
        self.username = username
        self.password = password
        self.is_admin = is_admin

# create tables
def create_db():
    Base.metadata.create_all(engine)


def populate_data():

    for key, value in fees.items():
        new_fee = Fees(name=key, fees_per_unit=value['fee'], unit_of_measure=value['unit'], weight=value['weight'])  
        session.add(new_fee)
    session.commit()

    for city in cities:
        new_city = City(city)
        session.add(new_city)
    session.commit()

    new_employee = Employee(username=root_user, password=root_password)
    session.add(new_employee)
    session.commit()