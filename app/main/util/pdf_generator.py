from flask import make_response

from .pdf.pdf_class import PDF
from .pdf.pdf_funs import generate_front_page, generate_visualizations


def send_pdf(user, diagnosis, name, locale):
    pdf = PDF(user, diagnosis)
    pdf = generate_front_page(pdf, diagnosis, name, locale)
    pdf = generate_visualizations(pdf, diagnosis, name, locale)

    #pdf.output('check.pdf', 'F')
    response = make_response(pdf.output(dest='S').encode('latin-1'))
    response.headers.set('Content-Disposition', 'attachment', filename='diagnosis.pdf')
    response.headers.set('Content-Type', 'application/pdf')
    return response
