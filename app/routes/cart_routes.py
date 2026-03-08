#app/routes/cart_routes.py

from flask import Blueprint, redirect, url_for, request, render_template
from flask_login import login_required
from app.models.medicine import Medicine
from app.services.cart_service import (
    add_to_cart,
    get_cart,
    remove_from_cart,
    cart_total,
    update_quantity
)

from app.utils.audit_logger import log_action


cart_bp = Blueprint("cart", __name__, url_prefix="/cart")


@cart_bp.route("/")
@login_required
def view_cart():

    cart = get_cart()
    total = cart_total()

    return render_template("main/cart.html", cart=cart, total=total)


@cart_bp.route("/add/<slug>", methods=["POST"])
@login_required
def add(slug):

    medicine = Medicine.objects(slug=slug).first()

    quantity = int(request.form.get("quantity", 1))

    add_to_cart(medicine, quantity)

    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/update/<slug>", methods=["POST"])
@login_required
def update(slug):

    quantity = int(request.form.get("quantity", 1))

    update_quantity(slug, quantity)

    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/remove/<slug>")
@login_required
def remove(slug):

    remove_from_cart(slug)

    return redirect(url_for("cart.view_cart"))