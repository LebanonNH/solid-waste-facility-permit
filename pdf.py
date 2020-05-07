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
        self.image('col-logo.png', 83, 8, w=50)
        self.set_font('Arial', 'B', 15)

        # Add an address
        self.ln(20)
        self.cell(0, 5, 'Landfill Permit', align="C", ln=1)

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
    return json.dumps({"message": msg})


def create_pdf(citizen):
    pdf = CustomPDF()
    # Create the special value {nb}
    pdf.alias_nb_pages()
    pdf.add_page(orientation='P')
    pdf.set_font('Times', '', 36)
    pdf.image(create_barcode(citizen.barcode), 8, 55, 200)
    pdf.ln(110)
    pdf.cell(20)
    pdf.cell(0, 20, txt="Issued to: {}".format(citizen.name), ln=1)
    pdf.cell(20)
    pdf.cell(0, 20, txt="Expiration Date: {}".format(citizen.expiration), ln=1)
    pdf.cell(20)
    pdf.cell(0, 20, txt="City of Origin: {}".format(citizen.city), ln=1)
    pdf.output("permit.pdf")
    return "permit.pdf"

def create_barcode(code):
    ean = barcode.get('ean13', code, writer=ImageWriter())
    filename = ean.save(barcode)
    return filename

if __name__ == '__main__':
    citizen = Citizen("Joe Blow", "05/05/2020", "Lebanon", "123456789101","example@example.com")
    create_pdf('permit.pdf', citizen)
