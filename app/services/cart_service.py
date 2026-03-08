#app/services/cart_service.py

from flask import session

def get_cart():
    return session.get("cart", {})


def add_to_cart(medicine, quantity):

    cart = session.get("cart", {})

    slug = medicine.slug

    if slug in cart:
        cart[slug]["quantity"] += quantity
    else:
        cart[slug] = {
            "name": medicine.name,
            "price": medicine.pricing.selling_price,
            "quantity": quantity,
            "image": medicine.image_url
        }

    session["cart"] = cart
    session.modified = True

def update_quantity(slug, quantity):

    cart = session.get("cart", {})

    if slug in cart:
        if quantity <= 0:
            del cart[slug]
        else:
            cart[slug]["quantity"] = quantity

    session["cart"] = cart
    session.modified = True


def remove_from_cart(slug):

    cart = session.get("cart", {})

    if slug in cart:
        del cart[slug]

    session["cart"] = cart
    session.modified = True


def cart_total():

    cart = session.get("cart", {})
    return sum(item["price"] * item["quantity"] for item in cart.values())


def cart_count():
    cart = session.get("cart", {})
    return sum(item["quantity"] for item in cart.values())