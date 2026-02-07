import os
from io import BytesIO
from decimal import Decimal
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from dotenv import load_dotenv

load_dotenv()

def money(x) -> str:
    if x is None:
        x = Decimal("0.00")
    return f"${Decimal(x):,.2f}"

def build_document_pdf(ro, customer, vehicle, document, line_items, title=None):
    business_name = os.getenv("BUSINESS_NAME", "Roane Diagnostics")
    phone = os.getenv("BUSINESS_PHONE", "")
    doc_title = title or document.doc_type.capitalize()

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, business_name)
    c.setFont("Helvetica", 10)
    y -= 16
    if phone:
        c.drawString(50, y, f"Phone: {phone}")
        y -= 18
    else:
        y -= 8

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, f"{doc_title} - RO #{ro.ro_number}")
    y -= 18

    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Customer: {customer.name}  |  Phone: {customer.phone or '-'}  |  Email: {customer.email or '-'}")
    y -= 14

    veh_line = f"Vehicle: {vehicle.year or ''} {vehicle.make or ''} {vehicle.model or ''} {vehicle.engine or ''}".strip()
    c.drawString(50, y, veh_line)
    y -= 14
    c.drawString(50, y, f"VIN: {vehicle.vin or '-'}  |  Mileage: {vehicle.odometer_last or '-'}")
    y -= 18

    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Type")
    c.drawString(110, y, "Description")
    c.drawRightString(470, y, "Qty")
    c.drawRightString(540, y, "Amount")
    y -= 10
    c.line(50, y, 560, y)
    y -= 14

    c.setFont("Helvetica", 10)
    for li in line_items:
        amount = (li.qty or 0) * (li.unit_price or 0)

        if y < 120:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 10)

        c.drawString(50, y, li.item_type)
        c.drawString(110, y, (li.description or "")[:70])
        c.drawRightString(470, y, f"{li.qty}")
        c.drawRightString(540, y, money(amount))
        y -= 12

    y -= 8
    c.line(350, y, 560, y)
    y -= 14
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(500, y, "Subtotal:")
    c.drawRightString(560, y, money(document.subtotal))
    y -= 14
    c.drawRightString(500, y, "Tax:")
    c.drawRightString(560, y, money(document.tax))
    y -= 16
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(500, y, "Total:")
    c.drawRightString(560, y, money(document.total))

    c.showPage()
    c.save()
    buf.seek(0)
    return buf


def build_invoice_pdf(ro, customer, vehicle, document, line_items):
    return build_document_pdf(ro, customer, vehicle, document, line_items, title="Invoice")
