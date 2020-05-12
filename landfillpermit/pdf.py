import datetime
import os
import requests
import barcode
import random
import json
from fpdf import FPDF
from dotenv import load_dotenv
from barcode.writer import ImageWriter
from landfillpermit.models import session, User, City
from jinja2 import Environment, FileSystemLoader
from landfillpermit import mg_domain, mg_api_key




class Citizen():
    def __init__(self, first_name, surname, city, email):
        self.first_name = first_name.title()
        self.surname = surname.title()
        self.city = self.__verify_city(city).title()
        self.email = email
        expiration = datetime.datetime.now() + datetime.timedelta(days=365)
        self.expiration = expiration.date().strftime("%m-%d-%Y") 
        self.barcode = self.__verify_barcode(str(random.randint(99999999999,1000000000000)))

    def __verify_barcode(self, barcode):
        full_code = create_barcode(barcode)
        query = session.query(User).filter(User.barcode == full_code).first()
        if query:
            self.__verify_barcode(str(random.randint(99999999999,1000000000000)))
        return full_code
    
    def __verify_city(self, city):
        query = session.query(City).filter(City.city_name == city.title()).first()
        if not query:
            raise NameError('{} is not an authorized city'.format(city))
        else:
            return query.city_name 

    def add_to_db(self, barcode = None, city = None, expiration = None, first_name = None, surname = None):
        if barcode == None:
            barcode = self.barcode 
        if city == None:
            city = self.city
        if expiration == None:
            expiration = self.expiration 
        if first_name == None:
            first_name = self.first_name 
        if surname == None:
            surname = self.surname
        query = session.query(User).filter(User.barcode == self.barcode).first()
        if query:
            raise ValueError("User has already exists database")
        city_id = session.query(City).filter(City.city_name == self.city.title()).first().id 
        expiration_date = datetime.datetime.strptime(self.expiration, "%m-%d-%Y")
        new_user = User(self.barcode, expiration_date, self.first_name, self.surname, city_id)

        session.add(new_user)
        print("New user added to session")
        session.commit()
        



class CustomPDF(FPDF):

    def header(self):
        # Set up a logo
        self.image(os.path.dirname(os.path.abspath(__file__)) + '/col-logo.png', 82.95, 60.8, w=50)
        self.set_font('Arial', 'B', 15)

        # Add an address
        self.ln(75)
        self.set_font("times", "", 20)
        self.cell(0, 10, 'SOLID WASTE'.upper(), align="C", ln=1)
        self.cell(0, 10, 'FACILITY PERMIT'.upper(), align="C", ln=1)

        # Line break
        self.ln(20)


def create_pdf(citizen):
    name = citizen.first_name.upper() + " " + citizen.surname.upper()
    pdf = CustomPDF()
    # Create the special value {nb}
    pdf.alias_nb_pages()
    pdf.add_page(['P',"mm", "letter"])
    pdf.set_font('Times', '', 12)
    pdf.set_line_width(5)
    pdf.rect(57.15,50.8,101.6,177.8)
    pdf.image('/tmp/barcode.png', 60.45, 110.8, 95)
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
    ean.save('/tmp/barcode')
    return ean.get_fullcode() 

def send_message(citizen, file):
    url = "https://api.mailgun.net/v3/" + mg_domain + "/messages"
    try:
        path = os.path.join(os.getcwd(), 'landfillpermit')
        env = Environment(loader=FileSystemLoader(path), autoescape=True)
    except:
        print("couldn't set template env")
    try:
        template = env.get_template('email.html')
    except:
        print("couldn't get template")

    try:
        req = requests.post(
            url,
            auth=("api", mg_api_key),
            files=[("attachment", ("permit.pdf", open(file,"rb").read()))],
            timeout=1,
            data={"from": "City of Lebanon Solid Waste <solid.waste@lebanonnh.gov>",
                "to": citizen.email,
                "subject": "Your Landfill Permit",
                "text": "Here is your permit",
                "html": template.render(citizen=citizen)})
        return req.status_code
    except:
        print("Something went wrong with the post request")

def permit(first_name, surname, email, city):
    citizen = Citizen(first_name, surname, city, email)
    pdf_path = create_pdf(citizen)
    msg = 'Created permit for {} {} and emailed it to {}'.format(first_name.title(), surname.title(), email)
    print(msg)
    citizen.add_to_db()
    send_message(citizen, pdf_path)
    body = {
        'message': msg, 
        'barcode': citizen.barcode,
        'expiration': citizen.expiration
        }
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(body)
        }