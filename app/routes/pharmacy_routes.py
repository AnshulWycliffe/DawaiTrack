#app/routes/pharmacy_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.medicine import Medicine, Pricing
from app.models.order import Order
from app.models.inventory_batch import InventoryBatch
from app.models.expired_medicine import ExpiredMedicineRequest
from app.config.constants import MEDICINE_CATEGORIES_UI, MEDICINE_CATEGORIES, ORDER_STATUS
from datetime import datetime
from app.extensions.decorator import role_required
from app.config.roles import Roles
from slugify import slugify
from app.utils.audit_logger import log_action


import os
from werkzeug.utils import secure_filename
from flask import current_app
import uuid


pharmacy_bp = Blueprint("pharmacy", __name__, url_prefix="/pharmacy")


UPLOAD_FOLDER = "app/static/uploads/medicines"


# -------------------------
# Add Medicine
# -------------------------

@pharmacy_bp.route("/medicines", methods=["GET", "POST"])
@login_required
@role_required(Roles.PHARMACY)
def medicines():
    
    medicines = Medicine.objects.order_by("-created_at")
    return render_template(
        "pharmacy/medicines.html",
        medicines=medicines
    )


@pharmacy_bp.route("/medicines/add", methods=["GET", "POST"])
@login_required
@role_required(Roles.PHARMACY)
def add_medicine():
    
    if request.method == "POST":
        pricing = Pricing(
            mrp=float(request.form.get("mrp")),
            selling_price=float(request.form.get("selling_price"))
        )

        image_file = request.files.get("image")

        filename = None

        if image_file and image_file.filename != "":
            

            filename = f"{uuid.uuid4().hex}_{secure_filename(image_file.filename)}"
            
            save_path = os.path.join(
                current_app.root_path,
                "static/uploads/medicines",
                filename
            )

            image_file.save(save_path)

        medicine = Medicine(
            name=request.form.get("name"),
            slug=slugify(request.form.get("name")),
            category=request.form.get("category"),
            manufacturer=request.form.get("manufacturer"),
            description=request.form.get("description"),
            pricing=pricing,
            image_url=f"uploads/medicines/{filename}",
            requires_prescription=bool(request.form.get("requires_prescription")),
            created_by=current_user
        )

        medicine.save()
        log_action(
            "CREATE_MEDICINE",
            "Medicine",
            medicine.id,
            f"{medicine.name} added"
        )
        flash("Medicine added successfully!", "success")
        return redirect(url_for("pharmacy.add_batch", medicine_id=medicine.id))
    return render_template(
        "pharmacy/add_medicine.html",
        MEDICINE_CATEGORIES=MEDICINE_CATEGORIES_UI
    )


@pharmacy_bp.route("/medicine/<medicine_id>/edit", methods=["GET", "POST"])
@login_required
@role_required(Roles.PHARMACY)
def edit_medicine(medicine_id):

    medicine = Medicine.objects.get(id=medicine_id)

    if request.method == "POST":

        medicine.name = request.form["name"]
        medicine.slug = slugify(request.form["name"])
        medicine.category = request.form["category"]
        medicine.manufacturer = request.form["manufacturer"]
        medicine.description = request.form["description"]

        medicine.pricing.mrp = float(request.form["mrp"])
        medicine.pricing.selling_price = float(request.form["selling_price"])

        medicine.requires_prescription = bool(
            request.form.get("requires_prescription")
        )

        medicine.is_active = bool(
            request.form.get("is_active")
        )

        medicine.save()

        flash("Medicine updated successfully", "success")

        return redirect(url_for("pharmacy.medicines"))

    return render_template(
        "pharmacy/edit_medicine.html",
        medicine=medicine,
        MEDICINE_CATEGORIES=MEDICINE_CATEGORIES
    )


@pharmacy_bp.route("/medicine/<medicine_id>/add-batch", methods=["GET", "POST"])
@login_required
@role_required(Roles.PHARMACY)
def add_batch(medicine_id):

    medicine = Medicine.objects.get(id=medicine_id)

    if request.method == "POST":

        batch = InventoryBatch(
            medicine=medicine,
            batch_number=request.form["batch_number"],
            expiry_date=request.form["expiry_date"],
            quantity=int(request.form["quantity"]),
            purchase_price=float(request.form["purchase_price"]),
            supplier=request.form["supplier"]
        )

        batch.save()

        log_action(
            "ADD_BATCH",
            "InventoryBatch",
            batch.id,
            f"Batch {batch.batch_number} added"
        )
        flash("Batch added successfully", "success")

        return redirect(url_for("pharmacy.inventory"))

    return render_template(
        "pharmacy/add_batch.html",
        medicine=medicine
    )

@pharmacy_bp.route("/inventory/<batch_id>/delete", methods=["POST"])
@login_required
@role_required(Roles.PHARMACY)
def delete_batch(batch_id):
    
    batch = InventoryBatch.objects.get(id=batch_id)

    batch.delete()
    log_action(
        "DELETE_BATCH",
        "InventoryBatch",
        batch.id,
        f"Batch {batch.batch_number} deleted"
    )
    flash("Batch deleted successfully")

    return redirect(url_for("pharmacy.inventory"))


@pharmacy_bp.route("/inventory", methods=["GET", "POST"])
@login_required
@role_required(Roles.PHARMACY)
def inventory():
    
    batches = InventoryBatch.objects.order_by("expiry_date")

    return render_template(
        "pharmacy/inventory.html",
        batches=batches
    )


@pharmacy_bp.route("/orders", methods=["GET", "POST"])
@login_required
@role_required(Roles.PHARMACY)
def orders():
    
    orders = Order.objects()
    return render_template(
        "pharmacy/orders.html",
        orders=orders
    )


@pharmacy_bp.route("/orders/<order_id>", methods=["GET", "POST"])
@login_required
@role_required(Roles.PHARMACY)
def order_detail(order_id):
    
    order = Order.objects(id=order_id).first()
    
    if request.method == "POST":
        status = request.form.get("status")

        order.status = status
        order.save()
        log_action(
            "ORDER_STATUS",
            "Order",
            order.id,
            f"Order status updated to {order.status} by the PHARMACY"
        )
        return redirect(url_for("pharmacy.orders"))

    return render_template(
        "pharmacy/order_detail.html",
        order=order
    )


@pharmacy_bp.route("/cancel_orders/<order_id>", methods=["POST"])
@login_required
@role_required(Roles.PHARMACY)
def cancel_order(order_id):
    
    order = Order.objects(id=order_id).first()
    
    order.status = ORDER_STATUS[5]
    order.save()

    log_action(
        "ORDER_CANCELLED",
        "Order",
        order.id,
        f"Order cancelled by the PHARMACY"
    )

    return redirect(url_for("pharmacy.orders"))

   
@pharmacy_bp.route("/expired-requests")
@login_required
@role_required(Roles.PHARMACY)
def expired_requests():
    
    requests = ExpiredMedicineRequest.objects.order_by("-created_at")

    return render_template(
        "pharmacy/expired_requests.html",
        requests=requests
    )

@pharmacy_bp.route("/expired-request/<request_id>", methods=["GET", "POST"])
@login_required
@role_required(Roles.PHARMACY)
def expired_request_detail(request_id):
    
    req = ExpiredMedicineRequest.objects.get(id=request_id)

    if request.method == "POST":

        new_status = request.form.get("status")

        req.status = new_status
        req.save()
        log_action(
            "EXPIRED_REQ_STATUS",
            "ExpiredMedicineRequest",
            req.id,
            f"Request for expired medicine take back status updated to {req.status} by the PHARMACY"
        )
        flash("Request status updated successfully", "success")

        return redirect(url_for("pharmacy.expired_requests"))

    return render_template(
        "pharmacy/expired_request_detail.html",
        request=req
    )


@pharmacy_bp.route("/expired/<request_id>/update", methods=["POST"])
@login_required
@role_required(Roles.PHARMACY)
def update_expired_status(request_id):
    
        
    req = ExpiredMedicineRequest.objects.get(id=request_id)

    req.status = request.form["status"]

    req.save()

    

    flash("Status updated")

    return redirect(url_for("pharmacy.expired_requests"))


@pharmacy_bp.route("/expired-request/collect/<id>", methods=["POST"])
@login_required
def collect_request(id):

    req = ExpiredMedicineRequest.objects.get(id=id)

    req.status = "COLLECTED"
    req.collected_by = current_user
    req.collected_at = datetime.utcnow()

    req.save()

    log_action(
        "COLLECT_EXPIRED_MEDICINE",
        "ExpiredRequest",
        req.id,
        f"Medicine collected by pharmacy"
    )

    return jsonify({"success": True})
