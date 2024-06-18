from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from random import sample
import os
from flask_wtf.csrf import CSRFProtect
from forms import Add_Coffee, Update_Price, Search_form
from flask_bootstrap import Bootstrap

app = Flask(__name__)

##Connect to Database;
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
API_KEY = os.environ.get("API_KEY")
csrf = CSRFProtect(app)
csrf.init_app(app)
db = SQLAlchemy()
db.init_app(app)
Bootstrap(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

        # Method 2. Altenatively use Dictionary Comprehension to do the same thing.

        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    form = Search_form()
    msg = request.args.get("message")
    cafe = db.session.execute(db.select(Cafe))
    all_cafe = cafe.scalars().all()
    return render_template("index.html", cafes=all_cafe, form= form, message= msg)


@app.route("/random", methods=["GET", "POST"])
def random():
    cafe = db.session.execute(db.select(Cafe))
    all_cafe = cafe.scalars().all()
    random_cafes = sample(all_cafe, 1)
    # return jsonify(cafes={"can_take_calls": random_cafe.can_take_calls,
    #                       "coffee_price": random_cafe.coffee_price,
    #                       "has_sockets": random_cafe.has_sockets,
    #                       "has_toilet": random_cafe.has_toilet,
    #                       "has_wifi": random_cafe.has_wifi,
    #                       # "id": random_cafe.id,
    #                       "amenities": {
    #                           "img_url": random_cafe.img_url,
    #                           "location": random_cafe.location,
    #                           "map_url": random_cafe.map_url,
    #                           "name": random_cafe.name,
    #                           "seats": random_cafe.seats
    #                       }
    #                       })
    return render_template("index.html", cafes=random_cafes)


@app.route("/all", methods=["GET", "POST"])
def all_cafes():
    form = Search_form()
    every_cafe = db.session.execute(db.select(Cafe).order_by(Cafe.name)).scalars().all()
    cafe_list = [cafe.to_dict() for cafe in every_cafe]
    return render_template("index.html", cafes=cafe_list, form=form)


@app.route("/search", methods=["GET", "POST"])
def search_cafe():
    form = Search_form()
    all_cafes = db.session.execute(db.select(Cafe)).scalars().all()
    if request.method == "POST":
        loc = request.form.get("location")
        if loc:
            location = loc.split(" ")[0]
            print(location)
            each_cafe = db.session.execute(
                db.select(Cafe).where(Cafe.location.ilike(f"%{location}%"))
            ).scalars().all()
            cafe_list = [cafe.to_dict() for cafe in each_cafe]
            all_cafe_location = db.session.execute(db.select(Cafe.location)).scalars().all()

            if location.lower() in [loc.lower().split(" ")[0] for loc in all_cafe_location]:
                return render_template("index.html", cafes=each_cafe, location=location, form=form)
            else:
                return render_template("index.html", cafes= all_cafes, location=None,
                                       error="Sorry! we don't have a cafe at that location.", form=form)
        else:
            return render_template("index.html", cafes= all_cafes, location=None, error="Please enter a location.",
                                   )
    return render_template("index.html", form=form)  # If GET request, render with CSRF token


@app.route("/add", methods=["GET", "POST"])
def add_cafe():
    if request.method == "POST":
        new_cafe = Cafe(
            can_take_calls=bool(request.form.get("can_take_calls")),
            coffee_price=request.form.get("coffee_price"),
            has_sockets=bool(request.form.get("has_sockets")),
            has_toilet=bool(request.form.get("has_toilet")),
            has_wifi=bool(request.form.get("has_wifi")),
            name=request.form.get("name"),
            img_url=request.form.get("img_url"),
            location=request.form.get("location"),
            map_url=request.form.get("map_url"),
            seats=request.form.get("seats")
        )
        db.session.add(new_cafe)
        db.session.commit()
        return render_template("index.html", message="Your cafe is successfully added")

    form = Add_Coffee()
    return render_template("index.html", aform= form)


@app.route("/update-price/<cafe_id>", methods=["PATCH", "GET", "POST"])
def update_data(cafe_id):
    cafes = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalars().all()
    cafe_loc = ""
    if request.method == "POST" or request.method == "PATCH":
        for cafe in cafes:
            cafe_loc = cafe.location
        new_price = request.form.get("new_price")
        cafe = db.get_or_404(Cafe, cafe_id)
        cafe.coffee_price = "£"+new_price
        db.session.commit()
        return render_template("index.html", cafe_id= cafe_id, cafes=cafes, location=cafe_loc)

    form = Update_Price()
    return render_template("index.html", myform= form, cafe_id= cafe_id)


@app.route("/report-closed/<cafe_id>", methods=["DELETE", "GET", "POST"])
def delete_cafe(cafe_id):
    print(request.method)
    print(request.args.get("api_key"))

    api_key = request.args.get("api_key")
    if str(api_key) == API_KEY:
        cafe_to_delete = db.get_or_404(Cafe, cafe_id)
        db.session.delete(cafe_to_delete)
        db.session.commit()
        return redirect(url_for("all_cafes"))

    else:
        return redirect(url_for("all_cafes"), message="Sorry! that's not allowed, Make sure you have the correct api_key.")


@app.route("/features/<cafe_id>", methods=["GET", "POST"])
def features(cafe_id):
    cafes = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalars().all()
    features = {}
    cafe_loc = ""
    form = Search_form()
    for cafe in cafes:
        features.update({
            "has_toilet": cafe.has_toilet,
            "seats": cafe.seats,
            "has_wifi": cafe.has_wifi,
            "has_sockets": cafe.has_sockets,
            "can_take_calls": cafe.can_take_calls,
        })
        cafe_loc = cafe.location

    return render_template("index.html", features= features, form= form, cafes= cafes, location=cafe_loc)





## HTTP GET - Read Record

## HTTP POST - Create Record

## HTTP PUT/PATCH - Update Record

## HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
