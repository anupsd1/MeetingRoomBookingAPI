from gen_invoice import InvoiceGenerator, Utility
import os
import pdfkit
from .utils import render_to_pdf
from datetime import datetime, timezone
from django.http import HttpResponse
from django.conf import settings
from django.template import Context
from django.template.loader import get_template
from xhtml2pdf import pisa
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from django.views import View

from django.views import View
from django.shortcuts import render



from django.core.files.storage import FileSystemStorage
from wsgiref.util import FileWrapper
from django.http import FileResponse

os.environ["INVOICE_LANG"] = "en"

# # Our output file paths
# OUTFILE_HTML = "output.html"
# OUTFILE_PDF = "output.pdf"
#
# # Load our template and stylesheet data from file
# template = Utility.read_file("template.html")
# stylesheet = Utility.read_file("styles.css")


# Generate our invoice
def letscreate():

    generator = InvoiceGenerator()
    generator.generate(

        # Our output HTML file
        outfile=OUTFILE_HTML,

        # Our invoice number
        number="INV001",

        # Our line items
        items=[
            {
                "Section": "Materials",
                "Item": "Widget A",
                "Quantity": "20",
                "Units": "pcs",
                "Price": "12.99"
            }
        ],

        # Our payee details
        payee={
            "name": "XYZ Widget Company",
            "identifier": "123456789",
            "email": "domestic@example.com",
            "address": [
                "1 Widget Road",
                "Widgetville",
                "WID 9999"
            ],
            "bank": {
                "holder": "XYZ Widget Company",
                "bank": "Acme Banking Co",
                "code": "123-456",
                "account": "192837465"
            }
        },

        # Our payer details
        payer={
            "name": "XYZ Widget Company",
            "address": [
                "1 Widget Road",
                "Widgetville",
                "WID 9999"
            ],
            "due": "Within 30 days of receipt"
        },

        # Our template and stylesheet
        template=template,
        stylesheet=stylesheet,

        # No tax
        tax=0.0,

        # Generate a domestic invoice rather than an international one
        is_international=False,

        # Generate an invoice rather than a quote
        is_quote=False
    )

    # Render the invoice HTML to a PDF file using electron-pdf
    # generator.render(OUTFILE_HTML, OUTFILE_PDF)
    pdfkit.from_file('template.html', 'out.pdf')


def letscreate2(mydata):
    if mydata:
        data = mydata
    else:
        data = {
            'today': datetime.now(timezone.utc),
            'amount': 39.99,
            'customer_name': 'Cooper Mann',
            'order_id': 1233434,
        }
    pdf = render_to_pdf('template.html', data)
    print("FOR PDF = ")
    for key, value in pdf.items():
        print("KEY=" + str(key))
        print("VALUE = " + str(value))
        print("\n")
    # return HttpResponse(pdf, content_type='application/pdf')
    # print("PDF_CONTENT = " + str(pdf.content))
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "MyInvoice_%s.pdf" % ("125")
        content = "attachment; filename='%s'" % (filename)
        response['Content-Length'] = len(response.content)
        # download = request.GET.get("download")
        # if download:
        #
        #     print("AFTER DOWNLOAD")
        #     response['Content-Length'] = len(response.content)
        #     content = "attachment; filename='%s'" % (filename)
        #     # response.content.decode('utf-8').strip()

        response['Content-Disposition'] = content
        for key, value in response.items():
            print("KEY=" + str(key))
            print("VALUE = " + str(value))
            print("\n")
        # print(*response)
        pdf.close()
        # response.close()
        return response
    return HttpResponse("Not found")
    print("OUTSIDE IF PDF")


# class DownloadPDF(View):
#     def get(self, request, *args, **kwargs):
#         data = {
#             'today': datetime.now(timezone.utc),
#             'amount': 39.99,
#             'customer_name': 'Cooper Mann',
#             'order_id': 1233434,
#         }
#         pdf = render_to_pdf('template.html', data)
#         if pdf:
#             response = HttpResponse(pdf, content_type='application/pdf')
#             filename = "MyInvoice_%s.pdf" % ("125")
#             content = "inline; filename='%s'" % (filename)
#             download = request.GET.get("download")
#             if download:
#                 print("AFTER DOWNLOAD")
#                 response['Content-Length'] = len(response.content)
#                 content = "attachment; filename='%s'" % (filename)
#                 # response.content.decode('utf-8').strip()
#             response['Content-Disposition'] = content


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    print("IN LINK CALLBACK! ")
    # use short variable names
    sUrl = settings.STATIC_URL      # Typically /static/
    sRoot = settings.STATIC_ROOT    # Typically /home/userX/project_static/
    mUrl = settings.MEDIA_URL       # Typically /static/media/
    mRoot = settings.MEDIA_ROOT     # Typically /home/userX/project_static/media/
    print(sUrl + sRoot + mUrl + mRoot)
    # convert URIs to absolute system paths
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri  # handle absolute uri (ie: http://some.tld/foo.png)
    # make sure that file exists
    if not os.path.isfile(path):
        print("INSIDE OS.PATH")
        raise ValidationError("MEDIA URL WMUST START WITH!! ")
        raise Exception(
                'media URI must start with %s or %s' % (sUrl, mUrl)
            )
    return path


def render_pdf_view(request):
    template_path = 'template.html'
    context = {'myvar': 'this is your template context'}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    # find the template and render it.
    my_template = get_template(template_path)
    html = my_template.render(context)
    print("DONE RENDERING??!!!")
    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)
    print(type(pisa_status))
    # if error then show some funy view
    if pisa_status.err:
        print("ERRORR!!!!!!")
        # return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


class NewAPIView(APIView):
    print("IN API VIEW")

    permission_classes = []

    def get(self, *args, **kwargs):
        data = {

        }
        pdf = render_to_pdf('template.html', data)

        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "MyInvoice_%s.pdf" % ("111")
            print("AFTER DOWNLOAD")
            response['Content-Length'] = len(response.content)
            print("USER = " + str(self.request.user))
            content = "attachment; filename=%s" % (filename)
            # response.content.decode('utf-8').strip()

            response['Content-Disposition'] = content
            # response.close()
            return response
        return HttpResponse("Not found")
        print("OUTSIDE IF PDF")


class NEWAPIView2(View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'template.html', context)
