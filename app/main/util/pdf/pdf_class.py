from fpdf import FPDF
from ..fun import age, decode_result

from flask.ext.babel import gettext


class PDF(FPDF):
    def __init__(self, user, diagnosis):
        super().__init__()
        self.user = user
        self.diagnosis = diagnosis
        self.add_font(
            'DejaVu', 
            '', 
            './app/main/util/pdf/fonts/DejaVuSansCondensed.ttf', 
            uni=True
        )
        self.add_font(
            'DejaVu', 
            'B', 
            './app/main/util/pdf/fonts/DejaVuSansCondensed-Bold.ttf', 
            uni=True
        )
        self.add_font(
            'DejaVu', 
            'I', 
            './app/main/util/pdf/fonts/DejaVuSansCondensed-Oblique.ttf', 
            uni=True
        )
    

    def header(self):
        # Logo
        self.image('./app/main/util/pdf/Logo.png', 5, 8, 53)
        # Arial bold 15
        self.set_font('DejaVu', '', 9)
        self.set_text_color(105, 105, 105)
        # Move to the right
        self.cell(120)
        # Title
        self.cell(30, 4, gettext('Patient: ') + self.user.first_name + ' ' + self.user.second_name)
        
        self.cell(-30)
        self.cell(0, 14, gettext('Patient username: @') + self.user.username)

        self.cell(-70)
        self.cell(0, 24, gettext('Patient age: ') + str(age(self.user.date_of_birth)))

        self.cell(-70)
        self.cell(0, 34, gettext('Result: ') + decode_result(
                self.diagnosis.result,
                scrape=False
            )
        )

        self.cell(-70)
        self.cell(0, 44, gettext('Date of diagnostics: ') +
            self.diagnosis.checked_on.strftime('%d.%m.%Y %H:%M:%S')
        )
        # Line break
        self.ln(10)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('DejaVu', 'I', 8)
        # Page number
        self.cell(0, 10, gettext('Page ') + str(self.page_no()) + '/{nb}', 0, 0, 'C')
