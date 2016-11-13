"""Bus Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, jsonify,render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import Stop, Bus, Rating, User, Bus_filter, Filter, connect_to_db, db
from math import acos, cos, radians
import reroute, requests


app = Flask(__name__)

app.secret_key = "ABC"

app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage"""

    buses = reroute.get_bus_list()
    html = render_template("homepage.html",
                        buses=buses)

    return html

@app.route('/stop_info', methods=['GET'])
def stop_info():
    latitude = request.args.get('lat')
    longitude = request.args.get('long')



    bus_stop_id = Stop.query.filter(Stop.stop_lat + .001400 >= latitude, 
                                    Stop.stop_lat - .001400 <= latitude, 
                                    Stop.stop_lon + .001400 >= longitude ,
                                    Stop.stop_lon - .001400 <= longitude).limit(3).all()

    stops = []

    for stop_info in bus_stop_id:
        stop_dict = stop_info.__dict__
        stop_id = stop_dict.get('stop_id')

        stops.append(stop_id)

    # reroute.get_stop_info(stops)

    url = reroute.get_stop_info(stops)
    xml = reroute.send_api(url)
    xml_bus_name = reroute.get_bus_name_info(xml)
    print xml_bus_name
    xml_stop_name = reroute.get_bus_stops(xml)
    print xml_stop_name
    xml_mins = reroute.get_bus_mins(xml)
    print xml_mins




    return render_template("bus_detail_geo.html", xml_bus_name=xml_bus_name, xml_stop_name=xml_stop_name,xml_mins=xml_mins)



@app.route('/bus_detail', methods=['GET'])
def bus_lists():
    """Bus detail page. Allows users to submit rating if logged in"""
    

    info = request.args.get('bus')
    bus_info = Bus.query.get(info)

    user_id = session.get("user_id")

    bus_dict = {'code': bus_info.bus_code, 
                'name': bus_info.bus_name,
                'lname': bus_info.bus_lname,
                'city': bus_info.city}

    rated_bus = bus_dict.get('name')


    # user_rating = Rating.query.filter_by(
    #         bus_code=rated_bus, user_id=user_id).first()


    result_dict = [u.__dict__ for u in Rating.query.filter_by(
            bus_code=rated_bus).all()]

    result_score =  [d['rating'] for d in result_dict]
    sessioned_bus_comments =  [d['comments'] for d in result_dict]

    print result_score

    comments =  db.session.query(Rating.comments).all()

    print 'COOOMMMENTS'
    print sessioned_bus_comments

  

   
    score_count = Rating.query.filter_by(
            bus_code=rated_bus).count()


    if score_count == 0:
        average = 'What, no rating? Well, rate this bus already!'
    else:
        average = reroute.get_rating_sum(result_score)/score_count
    session['bus_dict'] = bus_dict

    return render_template("bus_detail.html", info=bus_info, average=average, 
                            sessioned_bus_comments=sessioned_bus_comments)



@app.route('/register', methods=['GET'])
def register_form():
    """Show form for user signup."""

    return render_template("sign_in_form.html") 



@app.route('/register', methods=['POST'])
def sign_up():
    """Sign up page."""

    email = request.form["email"]
    password = request.form["password"]
    fname = request.form["first_name"]
    lname = request.form["last_name"]

    new_user = User(email=email, password=password, 
                fname=fname, lname=lname)

    db.session.add(new_user)
    db.session.commit()

    flash("User %s added." % fname)

    return redirect("/")


@app.route('/login', methods=['GET'])
def login():
    """Show login form."""



    return render_template("log_in_form.html")


@app.route('/login', methods=['POST'])
def login_process():
    """Process login."""

    
    email = request.form["email"]
    password = request.form["password"]

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("No such user")
        return redirect("/register")

    if user.password != password:
        flash("Incorrect password")
        return redirect("/login")

    session["user_id"] = user.user_id

    flash("Logged in")
    return redirect("/")
    return render_template("homepage.html")



@app.route('/logout')
def logout_process():
    """Log out"""

    del session["user_id"]
    flash("Logged Out.")
    return redirect("/")



@app.route('/ratings', methods=['GET'])
def rate():
    """Show rating page"""

    bus_dict = session.get('bus_dict')
    rated_bus = bus_dict.get('name')
    user_id = session.get("user_id")


    if user_id:
        user_rating = Rating.query.filter_by(
            bus_code=rated_bus, user_id=user_id).first()

    else:
        user_rating = None

    return render_template("ratings.html",
                           rated_bus=rated_bus,
                           user_rating=user_rating)




@app.route('/ratings', methods=['POST'])
def rate_process():
    """Submit Ratings."""

    user_id = session.get("user_id")
    bus_dict = session.get('bus_dict')
  

    rated_bus = bus_dict.get('name')


    if user_id:
        user_rating = Rating.query.filter_by(
            bus_code=rated_bus, user_id=user_id).first()

    else:
        user_rating = None

    filters = request.form.getlist("filters")

    
    comments = request.form["comments"]
    score = request.form["rating"]

    comment_info = Rating(comments=comments, rating=score, user_id=user_id, bus_code=rated_bus)


    for item in filters:
        bus_filter = Bus_filter(filter_code=item, user_id=user_id, bus_code=rated_bus)
        db.session.add(bus_filter)



    db.session.add(comment_info)
    db.session.commit()

    return redirect("/bus_detail" + "?bus=" + rated_bus)






if __name__ == "__main__":
 
    app.debug = True
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)


    
    app.run(port=5000, host="0.0.0.0")

