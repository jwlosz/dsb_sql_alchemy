# Import the dependencies.
from flask import Flask, jsonify
import pandas as pd
import numpy as np

import datetime as dt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################

#creating engine
engine = create_engine("sqlite:///C:/Users/jwlos/OneDrive/Desktop/Bootcamp/Homework/dsb_sql_alchemy/Starter_Code/Resources/hawaii.sqlite")

# declaring base 
Base = automap_base()

#use base to reflect database
Base.prepare(autoload_with=engine)

#assigning variables for variable classes
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

#establishing inital flask route for app landing
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate API - This is desiged to return Station Data for Analysis <br/>"
        f"Available Links: <br/>"
        f"/api/v1.0/percipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' date need to be in the format MMDDYYYY.<p/>"
    )

#establishing flask links/routes
#precipiration route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the prior year"""
    # calculate year prior from last date in database
    prior_yr = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #query based on date for precipitation for last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prior_yr).all()

    session.close()
    #dictionary with date as key and prcp as value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

#stations route
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""
    results = session.query(Station.station).all()
    session.close()

    # recieving results - unravel into array - convert to list
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

#tobs route
@app.route("/api/v1.0/tobs")
def temp_month():
    "Return the Temp observations (TOBS) for prior year."""
    #calculation prior year date for TOBS
    prior_yr = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #query station for all tabs in prior year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prior_yr).all()
    session.close()


    # recieving results - unravel into array - convert to list
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

#temp start and end routes
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

    #statement selection
    select = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")
        # calculate the return values for dates greater than the start
        results = session.query(*select).\
            filter(Measurement.date >= start).all()
        
        session.close()

        # unravel into array and convert to list
        temps = list(np.ravel(results))
        return jsonify(temps=temps)

    # calculate tmin, tavg, tmax with start and end dates
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")

    results = session.query(*select).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    session.close()


    # unravel into array and convert to list
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

if __name__ == '__main__':
    app.run()