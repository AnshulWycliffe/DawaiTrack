#app/routes/order_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, session, abort, send_file,flash
from flask_login import login_required, current_user
from app.services.cart_service import get_cart, cart_total
from app.models.order import Order, OrderItem
from app.models.medicine import Medicine
from app.services.inventory_service import deduct_stock,check_stock
from app.config.constants import ORDER_STATUS
from app.utils.audit_logger import log_action


order_bp = Blueprint("order", __name__, url_prefix="/order")


@order_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():

    cart = get_cart()

    if not cart:
        return redirect(url_for("cart.view_cart"))

    total = cart_total()

    if request.method == "POST":

        address = request.form.get("address")
        payment_method = request.form.get("payment_method")

        order_items = []

        for item in cart.values():

            medicine = Medicine.objects(name=item["name"]).first()
            qty = item["quantity"]

            if not medicine or not check_stock(medicine,qty):
                flash("Insufficient stock","warning")
                return "Insufficient stock", 400


            deduct_stock(medicine, qty)
            
            
            medicine.save()

            order_items.append(
                OrderItem(
                    name=item["name"],
                    price=item["price"],
                    quantity=item["quantity"]
                )
            )

        order = Order(
            user=current_user,
            items=order_items,
            total_amount=total,
            payment_method=payment_method,
            address=address
        )

        order.save()
        log_action(
            "ORDER_PLACED",
            "Order",
            order.id,
            f"Order placed with total ₹{order.total_amount}"
        )
        # Clear Cart
        session.pop("cart", None)

        return redirect(url_for("order.success", order_id=str(order.id)))

    return render_template("main/checkout.html", cart=cart, total=total)


@order_bp.route("/success/<order_id>")
@login_required
def success(order_id):

    order = Order.objects(id=order_id).first()

    return render_template("main/order_success.html", order=order)


@order_bp.route("/history")
@login_required
def history():

    orders = Order.objects(
        user=current_user
    ).order_by("-created_at")

    return render_template(
        "main/order_history.html",
        orders=orders,
        STATUS_COLORS = {
        "PLACED": "bg-success",
        "CANCELLED": "bg-danger",
        "SHIPPED": "bg-info",
        "DELIVERED": "bg-primary"
    }
    )


@order_bp.route("/detail/<order_id>")
@login_required
def detail(order_id):

    order = Order.objects(
        id=order_id,
        user=current_user
    ).first()

    if not order:
        abort(404)

    return render_template(
        "main/order_detail.html",
        order=order
        
    )


@order_bp.route("/cancel/<order_id>")
@login_required
def cancel(order_id):

    order = Order.objects(
        id=order_id,
        user=current_user
    ).first()

    if not order or order.status != ORDER_STATUS[1]:
        return "Cannot cancel this order", 400

    # Restore stock
    from app.models.medicine import Medicine

    for item in order.items:

        medicine = Medicine.objects(name=item.name).first()

        if medicine:
            deduct_stock(medicine,item.quantity)
            medicine.save()

    order.status = ORDER_STATUS[5]
    order.save()
    log_action(
        "ORDER_CANCELLED",
        "Order",
        order.id,
        f"Order cancelled by customer side #{order.user.name}"
    )

    return redirect(url_for("order.history"))


import os
from flask import Blueprint, abort, send_file
from flask_login import login_required, current_user
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate,
    Paragraph, Spacer, Table, TableStyle, HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas



# ── Colour palette ────────────────────────────────────────────────────────────
_DARK_NAVY   = colors.HexColor("#0D1B2A")
_MID_GREY    = colors.HexColor("#6B7280")
_LIGHT_GREY  = colors.HexColor("#F3F4F6")
_BORDER_GREY = colors.HexColor("#D1D5DB")
_ACCENT      = colors.HexColor("#1D4ED8")
_BLACK       = colors.HexColor("#111827")
_PAGE_W, _PAGE_H = A4
_MARGIN = 0.75 * inch


# ── Canvas chrome (header bar + footer) ──────────────────────────────────────
def _draw_page_chrome(c: canvas.Canvas, doc):
    c.saveState()

    # Top navy bar
    c.setFillColor(_DARK_NAVY)
    c.rect(0, _PAGE_H - 0.55 * inch, _PAGE_W, 0.55 * inch, fill=1, stroke=0)

    # Company name
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(_MARGIN, _PAGE_H - 0.37 * inch, "DawaiTrack")

    # Tagline
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#93C5FD"))
    c.drawString(_MARGIN, _PAGE_H - 0.50 * inch, "Your Trusted Online Pharmacy")

    # "INVOICE" stamp
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(colors.HexColor("#60A5FA"))
    c.drawRightString(_PAGE_W - _MARGIN, _PAGE_H - 0.42 * inch, "INVOICE")

    # Footer rule
    c.setStrokeColor(_BORDER_GREY)
    c.setLineWidth(0.5)
    c.line(_MARGIN, 0.55 * inch, _PAGE_W - _MARGIN, 0.55 * inch)

    # Footer text
    c.setFont("Helvetica", 7.5)
    c.setFillColor(_MID_GREY)
    c.drawString(
        _MARGIN, 0.35 * inch,
        "DawaiTrack · support@dawaitrack.com · www.dawaitrack.com",
    )
    c.drawRightString(
        _PAGE_W - _MARGIN, 0.35 * inch,
        "This is a computer-generated invoice and requires no signature.",
    )

    c.restoreState()


# ── PDF builder ───────────────────────────────────────────────────────────────
def _build_invoice(file_path: str, order: Order) -> None:
    """Render a professional A4 invoice PDF for *order* at *file_path*."""

    doc = BaseDocTemplate(
        file_path,
        pagesize=A4,
        leftMargin=_MARGIN,
        rightMargin=_MARGIN,
        topMargin=0.85 * inch,
        bottomMargin=0.75 * inch,
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates([
        PageTemplate(id="main", frames=[frame], onPage=_draw_page_chrome)
    ])

    base_styles = getSampleStyleSheet()

    def S(name, **kw):
        return ParagraphStyle(name, parent=base_styles["Normal"], **kw)

    label_s  = S("Lbl",  fontSize=7.5, textColor=_MID_GREY,  leading=11, fontName="Helvetica")
    value_s  = S("Val",  fontSize=9.5, textColor=_BLACK,     leading=13, fontName="Helvetica-Bold")
    norm_s   = S("Nrm",  fontSize=9,   textColor=_BLACK,     leading=13)
    right_s  = S("Rt",   fontSize=9,   textColor=_BLACK,     leading=13, alignment=TA_RIGHT)
    tot_lbl  = S("TL",   fontSize=9,   textColor=_MID_GREY,  leading=14, alignment=TA_RIGHT)
    gnd_lbl  = S("GL",   fontSize=10,  textColor=_BLACK,     leading=15, fontName="Helvetica-Bold", alignment=TA_RIGHT)
    gnd_val  = S("GV",   fontSize=10,  textColor=_ACCENT,    leading=15, fontName="Helvetica-Bold", alignment=TA_RIGHT)
    hdr_l    = S("HL",   fontSize=8.5, textColor=colors.white, leading=12, fontName="Helvetica-Bold")
    hdr_r    = S("HR",   fontSize=8.5, textColor=colors.white, leading=12, fontName="Helvetica-Bold", alignment=TA_RIGHT)
    paid_s   = S("Paid", fontSize=8,   textColor=colors.white, fontName="Helvetica-Bold",
                         backColor=colors.HexColor("#16A34A"), borderPadding=(2, 6, 2, 6))

    # Resolve values from MongoEngine document
    invoice_no  = f"#{str(order.id).upper()}"
    invoice_date = order.created_at.strftime("%d %b %Y")
    customer    = order.user.name
    address     = order.address
    email       = getattr(order.user, "email", "N/A")
    total       = float(order.total_amount)
    
    elements = []

    # ── Meta block ────────────────────────────────────────────────────────────
    def _flat(rows):
        t = Table(rows, colWidths=[2.8 * inch])
        t.setStyle(TableStyle([
            ("LEFTPADDING",  (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING",   (0, 0), (-1, -1), 1),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 1),
        ]))
        return t

    left_block = _flat([
        [Paragraph("INVOICE NUMBER", label_s)],
        [Paragraph(invoice_no, value_s)],
        [Spacer(1, 6)],
        [Paragraph("INVOICE DATE", label_s)],
        [Paragraph(invoice_date, value_s)],
        [Spacer(1, 6)],
        [Paragraph("PAYMENT STATUS", label_s)],
        [Paragraph("PAID", paid_s)],
    ])

    right_block = _flat([
        [Paragraph("BILLED TO", label_s)],
        [Paragraph(customer, value_s)],
        [Paragraph(address, norm_s)],
        [Spacer(1, 6)],
        [Paragraph("CONTACT", label_s)],
        [Paragraph(email, norm_s)],
    ])

    meta = Table([[left_block, right_block]], colWidths=[3.0 * inch, 3.75 * inch], hAlign="LEFT")
    meta.setStyle(TableStyle([
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
    ]))

    elements += [meta, Spacer(1, 0.3 * inch),
                 HRFlowable(width="100%", thickness=0.5, color=_BORDER_GREY),
                 Spacer(1, 0.25 * inch)]

    # ── Items table ───────────────────────────────────────────────────────────
    col_w = [3.35 * inch, 1.15 * inch, 0.65 * inch, 1.1 * inch]

    rows = [[
        Paragraph("DESCRIPTION", hdr_l),
        Paragraph("UNIT PRICE",  hdr_r),
        Paragraph("QTY",         hdr_r),
        Paragraph("AMOUNT",      hdr_r),
    ]]

    for item in order.items:
        unit  = float(item.price)
        qty   = int(item.quantity)
        rows.append([
            Paragraph(item.name, norm_s),
            Paragraph(f"Rs. {unit:,.2f}",        right_s),
            Paragraph(str(qty),                   right_s),
            Paragraph(f"Rs. {unit * qty:,.2f}",  right_s),
        ])

    items_tbl = Table(rows, colWidths=col_w, repeatRows=1)
    items_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  _DARK_NAVY),
        ("ROWBACKGROUND", (0, 1), (-1, -1), [_LIGHT_GREY, colors.white]),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("LINEBELOW",     (0, 0), (-1, 0),  0.5, colors.HexColor("#374151")),
        ("LINEBELOW",     (0, 1), (-1, -1), 0.3, _BORDER_GREY),
        ("LINEAFTER",     (0, 0), (-2, -1), 0.3, _BORDER_GREY),
        ("BOX",           (0, 0), (-1, -1), 0.5, _BORDER_GREY),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))

    elements += [items_tbl, Spacer(1, 0.3 * inch)]

    # ── Totals block ──────────────────────────────────────────────────────────
    totals_tbl = Table([
        ["", Paragraph("Subtotal",           tot_lbl), Paragraph(f"Rs. {total:,.2f}", right_s)],
        ["", Paragraph("Delivery",           tot_lbl), Paragraph("FREE",              right_s)],
        ["", Paragraph("Tax (0%)",           tot_lbl), Paragraph("Rs. 0.00",          right_s)],
        ["", Paragraph("<b>Grand Total</b>", gnd_lbl), Paragraph(f"Rs. {total:,.2f}", gnd_val)],
    ], colWidths=[3.5 * inch, 1.4 * inch, 1.35 * inch])

    totals_tbl.setStyle(TableStyle([
        ("ALIGN",         (0, 0), (-1, -1), "RIGHT"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ("LINEABOVE",     (1, 3), (-1, 3),  0.75, _DARK_NAVY),
        ("BOX",           (1, 0), (-1, -1), 0.5,  _BORDER_GREY),
        ("LINEBELOW",     (1, 0), (-1, 2),  0.3,  _BORDER_GREY),
        ("BACKGROUND",    (1, 3), (-1, 3),  colors.HexColor("#EFF6FF")),
    ]))

    elements += [totals_tbl, Spacer(1, 0.45 * inch)]

    # ── Notes / Terms ─────────────────────────────────────────────────────────
    elements += [
        HRFlowable(width="100%", thickness=0.5, color=_BORDER_GREY),
        Spacer(1, 0.15 * inch),
    ]

    notes_tbl = Table([[
        Paragraph(
            "<b>Notes</b><br/>Thank you for choosing DawaiTrack! "
            "All medicines are sourced from licensed distributors and stored "
            "under recommended conditions.",
            norm_s,
        ),
        Paragraph(
            "<b>Payment Terms</b><br/>Payment due upon receipt. "
            "For queries contact support@dawaitrack.com or call 1800-XXX-XXXX.",
            norm_s,
        ),
    ]], colWidths=[3.4 * inch, 3.1 * inch])

    notes_tbl.setStyle(TableStyle([
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
    ]))

    elements.append(notes_tbl)
    doc.build(elements)


# ── Flask route ───────────────────────────────────────────────────────────────
@order_bp.route("/invoice/<order_id>")
@login_required
def invoice(order_id):
    # Fetch order – must belong to the logged-in user
    order = Order.objects(id=order_id, user=current_user).first()
    if not order:
        abort(404)

    # Ensure invoices directory exists
    invoice_dir = os.path.join(os.getcwd(), "invoices")
    os.makedirs(invoice_dir, exist_ok=True)

    file_path = os.path.join(invoice_dir, f"invoice_{order.id}.pdf")

    # (Re-)generate the PDF
    _build_invoice(file_path, order)
    log_action(
        "INVOICE_GENERATED",
        "Order",
        order.id,
        f"Invoice generate"
    )
    return send_file(
        file_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"JeevanMeds_Invoice_{order.id}.pdf",
    )

