from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), dest=result)
    # print("RESULT.getValue() = " + str(result.getvalue()))
    if not pdf.err:
        print("NO ERROR.....")
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
