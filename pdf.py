import datetime
import barcode
import random
import json
from fpdf import FPDF
from barcode.writer import ImageWriter

class Citizen():
    def __init__(self, name, city, email):
        self.name = name
        self.city = city
        self.email = email
        expiration = datetime.datetime.now() + datetime.timedelta(days=365)
        self.expiration = expiration.date().strftime("%m-%d-%Y") 
        self.barcode = str(random.randint(99999999999,1000000000000))


class CustomPDF(FPDF):

    def header(self):
        # Set up a logo
        self.image('col-logo.png', 82.95, 15, w=50)
        self.set_font('Arial', 'B', 15)

        # Add an address
        self.ln(25)
        self.set_font("times", "", 20)
        self.cell(0, 10, 'Residential'.upper(), align="C", ln=1)
        self.cell(0, 10, 'Landfill Permit'.upper(), align="C", ln=1)

        # Line break
        self.ln(20)

def permit(event, context):
    body = json.loads(event['body'])
    name = body['name']
    email = body['email']
    city = body['city']
    citizen = Citizen(name, city, email)
    pdf_path = create_pdf(citizen)
    msg = 'Created permit for {}, with barcode number {} and expiration of {} and emailed it to {}'.format(name, citizen.barcode, citizen.expiration, email)
    print(msg)
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': msg
        }

def create_pdf(citizen):
    pdf = CustomPDF()
    # Create the special value {nb}
    pdf.alias_nb_pages()
    pdf.add_page(['P',"mm", "letter"])
    pdf.set_font('Times', '', 12)
    pdf.set_line_width(5)
    pdf.rect(57.15,5,101.6,177.8)
    pdf.image(create_barcode(citizen.barcode), 60.45, 60, 95)
    pdf.ln(45)
    pdf.cell(50)
    pdf.cell(100, txt="Issued to: {}".format(citizen.name.upper()), ln=1)
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

