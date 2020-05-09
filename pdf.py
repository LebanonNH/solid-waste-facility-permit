import datetime
import os
import requests
import barcode
import random
import json
from fpdf import FPDF
from dotenv import load_dotenv
from barcode.writer import ImageWriter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.automap import automap_base


load_dotenv()
engine = create_engine(os.getenv('DB_PATH'))
Base = automap_base()
Base.prepare(engine, reflect=True)
User = Base.classes.user
City = Base.classes.city
session = Session(engine)

class Citizen():
    def __init__(self, first_name, surname, city, email):
        self.first_name = first_name
        self.surname = surname
        self.city = self.__verify_city(city)
        self.email = email
        expiration = datetime.datetime.now() + datetime.timedelta(days=365)
        self.expiration = expiration.date().strftime("%m-%d-%Y") 
        self.barcode = self.__verify_barcode(str(random.randint(99999999999,1000000000000)))
        self.__add_to_db()

    def __verify_barcode(self, barcode):
        query = session.query(User).filter(User.barcode == barcode).first()
        if query:
            self.__verify_barcode(str(random.randint(99999999999,1000000000000)))
        return barcode
    
    def __verify_city(self, city):
        query = session.query(City).filter(City.city_name == city.title()).first()
        if not query:
            raise NameError('{} is not an authorized city'.format(city))
        else:
            return query.city_name 

    def __add_to_db(self):
        city_id = session.query(City).filter(City.city_name == self.city.title()).first().id 
        new_user = User(self.barcode, self.expiration, self.first_name, self.surname, city_id)
        session.add(new_user)
        session.commit()
        



class CustomPDF(FPDF):

    def header(self):
        # Set up a logo
        self.image('col-logo.png', 82.95, 60.8, w=50)
        self.set_font('Arial', 'B', 15)

        # Add an address
        self.ln(75)
        self.set_font("times", "", 20)
        self.cell(0, 10, 'Residential'.upper(), align="C", ln=1)
        self.cell(0, 10, 'Landfill Permit'.upper(), align="C", ln=1)

        # Line break
        self.ln(20)

def permit(event, context):
    body = json.loads(event['body'])
    first_name = body['first_name']
    surname = body['surname']
    email = body['email']
    city = body['city']
    citizen = Citizen(first_name, surname, city, email)
    pdf_path = create_pdf(citizen)
    msg = 'Created permit for {}, with barcode number {} and expiration of {} and emailed it to {}'.format(name.title(), citizen.barcode, citizen.expiration, email)
    print(msg)
    send_message(email, pdf_path)
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': msg
        }

def create_pdf(citizen):
    name = citizen.first_name.upper() + " " + citizen.surname.upper()
    pdf = CustomPDF()
    # Create the special value {nb}
    pdf.alias_nb_pages()
    pdf.add_page(['P',"mm", "letter"])
    pdf.set_font('Times', '', 12)
    pdf.set_line_width(5)
    pdf.rect(57.15,50.8,101.6,177.8)
    pdf.image(create_barcode(citizen.barcode), 60.45, 110.8, 95)
    pdf.ln(45)
    pdf.cell(50)
    pdf.cell(100, txt="Issued to: {}".format(name, ln=1))
    pdf.ln(10)
    pdf.cell(50)
    pdf.cell(100, txt="Origin: {}".format(citizen.city.upper()), ln=1)
    pdf.ln(5)
    pdf.cell(50)
    pdf.cell(100, txt="Expiration Date: {}".format(citizen.expiration), ln=1)
    pdf.ln(20)
    pdf.set_font('Times', '', 12)
    pdf.cell(0, txt="Lebanon Solid Waste Facility", align="C")
    pdf.ln(5)
    pdf.cell(0, txt="370 Plainfield Road, West Lebanon, NH 03784", align="C")
    pdf.ln(5)
    pdf.cell(0, txt="603-298-6486 | LebanonNH.gov/SolidWaste", align="C")
    pdf.output("/tmp/permit.pdf")
    return "/tmp/permit.pdf"

def create_barcode(code):
    ean = barcode.get('ean13', code, writer=ImageWriter())
    filename = ean.save('/tmp/barcode')
    return filename 

def send_message(email, file):
    mg_domain = os.getenv('MG_DOMAIN')
    api_key = os.getenv('MG_API_KEY')
    url = "https://api.mailgun.net/v3/" + mg_domain + "/messages"

    return requests.post(
        url,
        auth=("api", api_key),
        files=[("attachment", ("permit.pdf", open(file,"rb").read()))],
        data={"from": "City of Lebanon Solid Waste <solid.waste@lebanonnh.gov>",
              "to": email,
              "subject": "Your Landfill Permit",
              "text": "Here is your permit",
              "html": "<html>Here is your permit!</html>"})
