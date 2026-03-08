#app/routes/admin_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.models.medicine import Medicine
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.expired_medicine import ExpiredMedicineRequest
from datetime import datetime


from app.utils.audit_logger import log_action


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


UPLOAD_FOLDER = "app/static/uploads/medicines"
# -------------------------
# Admin Dashboard
# -------------------------

from collections import Counter

@admin_bp.route("/dashboard")
@login_required
def dashboard():

    total_users = User.objects.count()
    total_pharmacies = User.objects(role="PHARMACY").count()
    total_medicines = Medicine.objects.count()

    # requests
    expired_requests = ExpiredMedicineRequest.objects()

    # pending disposal
    pending_disposal = ExpiredMedicineRequest.objects(
        status="COLLECTED"
    ).count()

    # disposal methods stats
    disposed = ExpiredMedicineRequest.objects(
        status="DISPOSED"
    )

    methods = [
        r.disposal_method
        for r in disposed
        if r.disposal_method
    ]

    method_counter = Counter(methods)

    disposal_labels = list(method_counter.keys())
    disposal_counts = list(method_counter.values())

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_pharmacies=total_pharmacies,
        total_medicines=total_medicines,
        pending_disposal=pending_disposal,
        disposal_labels=disposal_labels,
        disposal_counts=disposal_counts
    )


@admin_bp.route("/audit-logs")
@login_required
def audit_logs():

    logs = AuditLog.objects().order_by("-created_at")

    return render_template(
        "admin/audit_logs.html",
        logs=logs
    )

@admin_bp.route("/disposal")
@login_required
def disposal_page():

    requests = ExpiredMedicineRequest.objects(
        status="COLLECTED"
    ).order_by("-updated_at")

    return render_template(
        "admin/disposal.html",
        requests=requests
    )

@admin_bp.route("/dispose", methods=["POST"])
@login_required
def dispose_medicine():

    req_id = request.form.get("request_id")
    method = request.form.get("method")

    req = ExpiredMedicineRequest.objects.get(id=req_id)

    req.status = "DISPOSED"
    req.disposal_method = method
    req.disposed_by = current_user
    req.disposed_at = datetime.utcnow()

    req.save()

    log_action(
        action="DISPOSE_MEDICINE",
        entity="ExpiredMedicineRequest",
        entity_id=req.id,
        description=f"{req.medicine_name} disposed via {method}"
    )

    flash("Medicine disposed successfully", "success")

    return redirect(url_for("admin.disposal_page"))

