# -*- encoding: utf-8 -*-

from reportlab.pdfgen import canvas
from django.http import HttpResponse


def pdf(request):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=somefilename.pdf'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello World")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    return response
