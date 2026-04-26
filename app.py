from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "tours_travels_secret_key_2024_xZ9!")

# ── Error Handlers ─────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="Page not found."), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message=str(e)), 500

# ── Sample Data ────────────────────────────────────────────────────────────────
DESTINATIONS = [
    {"id":1,"name":"Bali, Indonesia","image":"https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800&q=80","price":1299,"duration":"7 Days / 6 Nights","category":"Beach","rating":4.8,"reviews":312,"description":"Experience the magic of Bali — lush rice terraces, ancient temples, vibrant nightlife, and pristine beaches all in one island paradise.","highlights":["Ubud Monkey Forest","Tanah Lot Temple","Seminyak Beach","Mount Batur Sunrise Trek"],"available_slots":12},
    {"id":2,"name":"Santorini, Greece","image":"https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800&q=80","price":2199,"duration":"6 Days / 5 Nights","category":"Cultural","rating":4.9,"reviews":487,"description":"Perched on volcanic cliffs above the Aegean Sea, Santorini's iconic white-washed buildings and sunsets are nothing short of legendary.","highlights":["Oia Sunset","Wine Tasting","Caldera Boat Tour","Ancient Akrotiri"],"available_slots":8},
    {"id":3,"name":"Machu Picchu, Peru","image":"https://images.unsplash.com/photo-1587595431973-160d0d94add1?w=800&q=80","price":1899,"duration":"8 Days / 7 Nights","category":"Adventure","rating":4.7,"reviews":256,"description":"Trek through the clouds to the Lost City of the Incas. One of the world's greatest archaeological wonders awaits at 2,430 metres above sea level.","highlights":["Inca Trail Trek","Sun Gate Viewpoint","Cusco City Tour","Sacred Valley"],"available_slots":15},
    {"id":4,"name":"Safari, Kenya","image":"https://images.unsplash.com/photo-1516426122078-c23e76319801?w=800&q=80","price":3499,"duration":"10 Days / 9 Nights","category":"Wildlife","rating":4.9,"reviews":198,"description":"Witness the Great Migration and come face-to-face with the Big Five in their natural habitat across the vast Maasai Mara and Amboseli plains.","highlights":["Great Migration","Big Five Safari","Maasai Village","Hot Air Balloon"],"available_slots":6},
    {"id":5,"name":"Kyoto, Japan","image":"https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&q=80","price":2499,"duration":"9 Days / 8 Nights","category":"Cultural","rating":4.8,"reviews":421,"description":"Step into Japan's ancient capital — a city where bamboo groves whisper beside golden temples and geishas still glide through lantern-lit alleyways.","highlights":["Fushimi Inari Shrine","Arashiyama Bamboo","Tea Ceremony","Nishiki Market"],"available_slots":10},
    {"id":6,"name":"Patagonia, Argentina","image":"https://images.unsplash.com/photo-1501854140801-50d01698950b?w=800&q=80","price":2799,"duration":"12 Days / 11 Nights","category":"Adventure","rating":4.6,"reviews":143,"description":"At the end of the world, raw nature reigns supreme. Towering granite spires, turquoise glacial lakes, and sweeping pampas define Patagonia's epic landscape.","highlights":["Torres del Paine Trek","Perito Moreno Glacier","Whale Watching","Gaucho Ranch"],"available_slots":20},
]

BOOKINGS = []

# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    categories = sorted(set(d["category"] for d in DESTINATIONS))
    return render_template("index.html", destinations=DESTINATIONS, categories=categories)

@app.route("/destination/<int:dest_id>")
def destination_detail(dest_id):
    dest = next((d for d in DESTINATIONS if d["id"] == dest_id), None)
    if not dest:
        flash("Destination not found.", "error")
        return redirect(url_for("index"))
    return render_template("detail.html", dest=dest)

@app.route("/book/<int:dest_id>", methods=["GET", "POST"])
def book(dest_id):
    dest = next((d for d in DESTINATIONS if d["id"] == dest_id), None)
    if not dest:
        return redirect(url_for("index"))
    if request.method == "POST":
        try:
            guests = int(request.form.get("guests", 1))
        except (ValueError, TypeError):
            guests = 1
        booking = {
            "id": len(BOOKINGS) + 1,
            "destination": dest["name"],
            "destination_id": dest_id,
            "name": request.form.get("name", ""),
            "email": request.form.get("email", ""),
            "phone": request.form.get("phone", ""),
            "guests": guests,
            "travel_date": request.form.get("travel_date", ""),
            "total": dest["price"] * guests,
            "booked_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "Confirmed",
        }
        BOOKINGS.append(booking)
        session["last_booking_id"] = booking["id"]
        return redirect(url_for("confirmation"))
    return render_template("book.html", dest=dest)

@app.route("/confirmation")
def confirmation():
    booking_id = session.get("last_booking_id")
    if not booking_id:
        return redirect(url_for("index"))
    booking = next((b for b in BOOKINGS if b["id"] == booking_id), None)
    if not booking:
        return redirect(url_for("index"))
    return render_template("confirmation.html", booking=booking)

@app.route("/my-bookings")
def my_bookings():
    return render_template("bookings.html", bookings=BOOKINGS)

@app.route("/api/search")
def search():
    q = request.args.get("q", "").lower()
    category = request.args.get("category", "")
    max_price = request.args.get("max_price", 99999, type=int)
    results = list(DESTINATIONS)
    if q:
        results = [d for d in results if q in d["name"].lower() or q in d["description"].lower()]
    if category:
        results = [d for d in results if d["category"] == category]
    results = [d for d in results if d["price"] <= max_price]
    return jsonify(results)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)