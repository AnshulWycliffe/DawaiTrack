# app/config/constants.py

ORDER_STATUS = [
    "PENDING",
    "PLACED",
    "CONFIRMED",
    "SHIPPED",
    "DELIVERED",
    "CANCELLED"
]

PICKUP_STATUS = [
    "REQUESTED",
    "COLLECTED",
    "DISPOSED"
]

PAYMENT_METHODS = [
    "COD",
    "UPI"
]

MEDICINE_CATEGORIES = ["WOMEN CARE",
                       "MEN CARE",
                       "KIDS CARE","HEART CARE",
                       "DIABETES CARE",
                       "IMMUNITY"]

MEDICINE_CATEGORIES_UI = [
    {"name": "WOMEN CARE", "icon": "bi-gender-female", "color": "bg-women"},
    {"name": "MEN CARE", "icon": "bi-gender-male", "color": "bg-men"},
    {"name": "KIDS CARE", "icon": "bi-emoji-smile", "color": "bg-kids"},
    {"name": "HEART CARE", "icon": "bi-heart-fill", "color": "bg-heart"},
    {"name": "DIABETES CARE", "icon": "bi-droplet-fill", "color": "bg-diabetes"},
    {"name": "IMMUNITY", "icon": "bi-shield-fill-check", "color": "bg-immunity"},
]

EXPIRED_REQUEST_STATUS = [
    "REQUESTED",
    "APPROVED",
    "COLLECTED",
    "DISPOSED"
]