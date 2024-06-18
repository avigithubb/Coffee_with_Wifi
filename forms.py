from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SearchField
from wtforms.validators import DataRequired, URL

class Add_Coffee(FlaskForm):
    can_take_calls = BooleanField("Can Take Calls: ")
    coffee_price = StringField("Coffee Price: ", render_kw={"placeholder": "Price in £"})
    has_sockets = BooleanField("Has Sockets: ")
    has_toilet = BooleanField("Has Toilet: ")
    has_wifi = BooleanField("Has Wifi")
    name = StringField("Name: ", validators=[DataRequired()], render_kw={"placeholder": "Your Name"})
    img_url = StringField("Image URL: ", validators=[DataRequired(), URL()], render_kw={"placeholder": "Only .jpg"})
    location = StringField("Location Name: ", validators=[DataRequired(), URL()], render_kw={"placeholder": "Cafe Location"})
    map_url = StringField("Map URL: ", validators=[DataRequired(), URL()], render_kw={"placeholder": "Ex.: https://www.maps.google.com"})
    seats = StringField("Seats: ", render_kw={"placeholder": "Ex: 3"}, validators=[DataRequired()])
    submit = SubmitField("Add")

class Update_Price(FlaskForm):
    new_price = StringField("Price: ")
    submit = SubmitField("Update")

class Search_form(FlaskForm):
    location = SearchField(label="", validators=[DataRequired()], render_kw={"placeholder": "Search for cafe location", "class": "search_input"})
    submit = SubmitField("search", render_kw={"id": "search_btn"})