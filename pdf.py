from fpdf import FPDF
import barcode
from barcode.writer import ImageWriter

class Citizen():
    def __init__(self, name, expiration, city, barcode):
        self.name = name
        self.expiration = expiration
        self.city = city
        self.barcode = barcode


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


def create_pdf(pdf_path, citizen):
    pdf = CustomPDF()
    # Create the special value {nb}
    pdf.alias_nb_pages()
    pdf.add_page(orientation='P')
    pdf.set_font('Times', '', 36)
    line_no = 1
    pdf.image(create_barcode(citizen.barcode), 8, 55, 200)
    pdf.ln(110)
    pdf.cell(20)
    pdf.cell(0, 20, txt="Issued to: {}".format(citizen.name), ln=1)
    pdf.cell(20)
    pdf.cell(0, 20, txt="Expiration Date: {}".format(citizen.expiration), ln=1)
    pdf.cell(20)
    pdf.cell(0, 20, txt="City of Origin: {}".format(citizen.city), ln=1)
    pdf.output(pdf_path)

def create_barcode(code):
    ean = barcode.get('ean13', code, writer=ImageWriter())
    filename = ean.save(code)
    return filename

if __name__ == '__main__':
    citizen = Citizen("Joe Blow", "05/05/2020", "Lebanon", "123456789012")
    create_pdf('permit.pdf', citizen)
