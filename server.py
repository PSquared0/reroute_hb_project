"""Bus Ratings."""
import os

from jinja2 import StrictUndefined

from flask import Flask, jsonify,render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import Stop, Bus, Rating, User, Bus_filter, Filter, connect_to_db, db
from math import acos, cos, radians
import reroute, requests
from sqlalchemy import func, desc

app = Flask(__name__)

app.secret_key = "ABC"

app.jinja_env.undefined = StrictUndefined




@app.route('/')
def home():
    """Homepage"""



    buses = reroute.get_bus_list()
    top_rated = db.session.query(Rating.bus_code).group_by(Rating.bus_code).order_by(desc(func.count(Rating.bus_code))).limit(10).all()
    



    user_id = session.get("user_id")
    if not user_id:
        return render_template('homepage.html', buses=buses, top_rated=top_rated)
    else:

        user = User.query.filter_by(user_id=user_id).one()

        print "xxxxx"
        print top_rated

        return render_template("homepage.html",
                            buses=buses, user=user, top_rated=top_rated)




@app.route('/stop_info', methods=['GET'])
def stop_info():
    latitude = request.args.get('lat')
    longitude = request.args.get('long')


    # latitude = 37.7993
    # longitude = -122.3977



    bus_stop_id = [u.__dict__ for u in Stop.query.filter(
                                                    Stop.stop_lat + .001400 >= latitude, 
                                                    Stop.stop_lat - .001400 <= latitude, 
                                                    Stop.stop_lon + .001400 >= longitude ,
                                                    Stop.stop_lon - .001400 <= longitude).limit(3).all()]




    info = reroute.get_stop_ids(bus_stop_id)
    urls = reroute.get_stop_info(info)
    xmls = reroute.send_api(urls)

    
    stop_dict = reroute.get_bus_name_info(xmls)
    print stop_dict

    if reroute.get_bus_name_info(xmls) is None:
        stop_dict = "Looks like muni doesn't run in your area, move to SF if you can afford it"
    else: 
        stop_dict = reroute.get_bus_name_info(xmls)


    user_id = session.get("user_id")

    if not user_id:
        return render_template("bus_detail_geo.html",stop_dict=stop_dict)
    else:

        user = User.query.filter_by(user_id=user_id).one()

        return render_template("bus_detail_geo.html",stop_dict=stop_dict, user=user,latitude=latitude, longitude=longitude )
    



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


    result_dict = [u.__dict__ for u in Rating.query.filter_by(
            bus_code=rated_bus).all()]

    result_score =  [d['rating'] for d in result_dict]
    sessioned_bus_comments =  [d['comments'] for d in result_dict]



    comments =  db.session.query(Rating.comments, User.fname).filter_by(bus_code=rated_bus).join(User).all()
    fils =  db.session.query(Bus_filter.filter_code).filter_by(bus_code=rated_bus).all()

      
    filters = []
    for fil in fils:
        n_filter = db.session.query(Filter.filter_name).filter_by(filter_code=fil).all()
        filters.append(n_filter)


    score_count = Rating.query.filter_by(
            bus_code=rated_bus).count()


    if score_count == 0:
        average = 'What, no rating? Well, rate this bus already!'
    else:
        average = reroute.get_rating_sum(result_score)/score_count

    session['bus_dict'] = bus_dict


    chart_dict = {}
    charts = db.session.query(Bus_filter, Filter).filter_by(bus_code=rated_bus).join(Filter).all()

    for chart in charts:
        count = chart_dict.get(chart[1].filter_name, 0)
        chart_dict[chart[1].filter_name] = count +1


    user_id = session.get("user_id")

    if not user_id:
        return render_template("bus_detail.html", info=bus_info, average=average,
                            sessioned_bus_comments=sessioned_bus_comments,
                            comments=comments, filters=filters, chart_dict=[chart_dict])
    else:

        user = User.query.filter_by(user_id=user_id).one()

        return render_template("bus_detail.html", info=bus_info, average=average,
                            sessioned_bus_comments=sessioned_bus_comments,
                            comments=comments, filters=filters, chart_dict=[chart_dict], user=user)



@app.route('/register', methods=['GET'])
def register_form():
    """Show form for user signup."""

    return render_template("sign_in_form.html") 



@app.route('/register', methods=['POST'])
def sign_up():
    """Sign up page."""

    email = request.form["email"]
    password = request.form["password"]
    password2 = request.form["password2"]
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

    user = User.query.filter_by(user_id=user_id).one()

    user_id = session.get("user_id")

    score = session.get("score")


    if not user_id:

        return render_template("ratings.html",
                           rated_bus=rated_bus,
                           user_rating=user_rating)
    else:

        return render_template("ratings.html",
                           rated_bus=rated_bus,
                           user_rating=user_rating, user=user, score=score)




@app.route('/ratings', methods=['POST'])
def rate_process():
    """Submit Ratings."""


    user_id = session.get("user_id")
    bus_dict = session.get('bus_dict')
  

    rated_bus = bus_dict.get('name')



    filters = request.form.getlist("filters")

    
    comments = request.form["comments"]
    score = request.form["rating"]

    comment_info = Rating(comments=comments, rating=score, user_id=user_id, bus_code=rated_bus)


    for item in filters:
        bus_filter = Bus_filter(filter_code=item, user_id=user_id, bus_code=rated_bus)
        db.session.add(bus_filter)

    user = User.query.filter_by(user_id=user_id).one()


    if score:
        score != None
        flash("Rating updated.")

    else:
        rating = comment_info
        flash("Rating added.")


    session["score"] = score

    db.session.add(comment_info)
    db.session.commit()

    return redirect("/bus_detail" + "?bus=" + rated_bus)


@app.route('/user', methods=['GET'])
def user():
    """Process login."""

    
    user_id = session.get("user_id")

    user_ratings = Rating.query.filter_by(user_id=user_id).all()
    user = User.query.filter_by(user_id=user_id).one()


    
    return render_template("user.html", user=user, user_ratings=user_ratings)





if __name__ == "__main__":

    connect_to_db(app, os.environ.get("DATABASE_URL"))

    # Create the tables we need from our models (if they already
    # exist, nothing will happen here, so it's fine to do this each
    # time on startup)
    # db.create_all(app=app)

    DEBUG = "NO_DEBUG" not in os.environ
    PORT = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)



    ####################################
 
    # app.debug = False
    # app.jinja_env.auto_reload = app.debug

    # connect_to_db(app)

    # # Use the DebugToolbar
    # DebugToolbarExtension(app)


    
    # app.run(port=5000, host="0.0.0.0")

