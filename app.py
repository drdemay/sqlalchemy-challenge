import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#create session link from Python to DB
session = Session(engine)

#####
# Flask Setup
app = Flask(__name__)

#####
# Flask Routes

@app.route("/")
def welcome():
    return (
        f"Ahoy! Welcome to the Aloha State Climate Analysis API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start</br>" 
        "----- Enter in your start date format = YYYY,%M,%D</br>"
        f"/api/v1.0/temp/start/end</br>" 
        "----- Enter in your start and end dates format = YYYY,%M,%D/YYYY,%M,%D"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    #Return precip data for the past year
    # Calculate the date 1 year ago from the last data point in the database
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation for the past year
    precipitation = session.query(Measurement.date,Measurement.prcp).\
        filter(Measurement.date >= year_ago).all()

    # Dictionary with date as the key and prcp as the value
    prcp = {date: prcp for date, prcp in precipitation}
    return jsonify(prcp)

@app.route("/api/v1.0/stations")
def stations():
    #gather station informaiton
    station_activity = session.query(Station.station).all()

    #convert station information to a list
    stations_list = list(np.ravel(station_activity))
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def temp_observations():
    # Provide the temp observations (tobs) for the previous year.
    # Calculate the date 1 year ago from the last data point in the database
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #gather tobs from the primary station
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= year_ago).all()
    
    # convert results to a list
    temps = list(np.ravel(results))
    # return results
    return jsonify(temps)



@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def dates(start=None, end=None):

    """
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """ 
 #   return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
  #      filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    selection = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    if not end:
        #calc min, max, avg for dates on or after start date
        results = session.query(*selection).\
            filter(Measurement.date >= start).all()

        #convert calc to a list 
        temps = list(np.ravel(results))
        return jsonify(temps)

    #calc min, max, avg for dates with start and stop dates
    results = session.query(*selection).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    # covert results to a list
    temps = list(np.ravel(results))
    return jsonify(temps)

if __name__ == '__main__':
    app.run()