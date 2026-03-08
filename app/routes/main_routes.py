#app/routes/main_routes.py

from flask import Blueprint, render_template, request,redirect,url_for,abort,flash
from flask_login import login_required,current_user
from app.models.medicine import Medicine
from app.models.expired_medicine import ExpiredMedicineRequest
from app.config.constants import MEDICINE_CATEGORIES_UI
from flask import jsonify

from app.utils.audit_logger import log_action


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():

    
    medicines = Medicine.objects(is_active=True)

    return render_template(
        "main/home.html",
        medicines=medicines,
        MEDICINE_CATEGORIES_UI=MEDICINE_CATEGORIES_UI
    )


@main_bp.route("/search")
def search():

    query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    price_range = request.args.get("price_range", "").strip()
    sort_by = request.args.get("sort", "").strip()

    filters = {
        "is_active": True
    }

    # 🔎 Name Search (Only for name, not category)
    if query:
        filters["name__icontains"] = query 
    
    # 🏷 Exact Category Match
    if category:
        filters["category"] = category   # exact match

    medicines = Medicine.objects(**filters)

    # 💰 Price Filtering
    if price_range:
        if price_range == "100":
            medicines = medicines.filter(
                pricing__selling_price__lte=100
            )
        elif price_range == "500":
            medicines = medicines.filter(
                pricing__selling_price__gte=100,
                pricing__selling_price__lte=500
            )
        elif price_range == "1000":
            medicines = medicines.filter(
                pricing__selling_price__gte=500
            )

    # 🔃 Sorting
    if sort_by == "low":
        medicines = medicines.order_by("pricing__selling_price")
    elif sort_by == "high":
        medicines = medicines.order_by("-pricing__selling_price")
    elif sort_by == "new":
        medicines = medicines.order_by("-created_at")

    return render_template(
        "main/search_results.html",
        medicines=medicines,
        MEDICINE_CATEGORIES_UI=MEDICINE_CATEGORIES_UI,
        search_query=query
    )


@main_bp.route("/api/search-suggestions")
def search_suggestions():

    query = request.args.get("q", "")

    if len(query) < 2:
        return jsonify([])

    medicines = Medicine.objects(
        name__icontains=query,
        is_active=True
    ).limit(5)

    results = [
        {
            "name": med.name,
            "slug": med.slug,
            "price": med.pricing.selling_price
        }
        for med in medicines
    ]

    return jsonify(results)


@main_bp.route("/product/<slug>")
def product_detail(slug):

    medicine = Medicine.objects(
        slug=slug,
        is_active=True
    ).first()

    if not medicine:
        abort(404)

    return render_template(
        "main/product_detail.html",
        medicine=medicine,
        MEDICINE_CATEGORIES_UI=MEDICINE_CATEGORIES_UI
    )


@main_bp.route("/submit-expired", methods=["GET", "POST"])
@login_required
def submit_expired_medicine():

    if request.method == "POST":

        req = ExpiredMedicineRequest(
            user=current_user,
            medicine_name=request.form["medicine_name"],
            expiry_date=request.form["expiry_date"],
            quantity=int(request.form["quantity"]),
            pickup_address=request.form["pickup_address"]
        )

        req.save()

        log_action(
            "REQUESTED_EXPIRED_MED_TAKE",
            "ExpiredMedicineRequest",
            req.id,
            f"Requested for expired medicine take back"
        )

        flash("Expired medicine request submitted")

        return redirect(url_for("main.expired_history"))

    return render_template("expired/submit_request.html")


@main_bp.route("/expired-medicine")
@login_required
def expired_history():

    requests = ExpiredMedicineRequest.objects(
        user=current_user
    ).order_by("-created_at")

    return render_template(
        "expired/request_history.html",
        requests=requests
    )
