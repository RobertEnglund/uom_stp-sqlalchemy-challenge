#################################################
# Dependencies
#################################################
from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
# home page
def welcome():
    return (
        f"Welcome to the home page<br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"<br/>"
        f" 1.  Precipitation by date:   /api/v1.0/precipitation<br/>"
        f" 2.  List of stations:        /api/v1.0/stations<br/>"
        f" 3.  Temperature by date:     /api/v1.0/tobs<br/>"
        f" 4.  Min/Avg/Max temps from start date (provide date as yyyy-mm-dd):   /api/v1.0/&lt;start&gt;<br/>"
        f" 5.  Min/Avg/Max temps between dates (provide dates as yyyy-mm-dd):    /api/v1.0/&lt;start&gt;/&lt;end&gt;"

    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Find most recent date
    session = Session(engine)
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    strdate = str(most_recent_date[0])

    # Calculate the date 1 year ago from the last data point in the database
    start_date = dt.datetime.strptime(strdate, "%Y-%m-%d") - dt.timedelta(days=366)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.prcp >=0).\
        filter(Measurement.date >= start_date).all()

    # Convert the query results to a dictionary using date as the key and prcp as the value.
    precip_list = []
    for i in results:
        precip_dict = {}
        precip_dict["Date"] = i[0]
        precip_dict["Precipitation"] = i[1]
        precip_list.append(precip_dict)

    # Return the JSON representation of your dictionary.    
    return jsonify(precip_list)

   
@app.route("/api/v1.0/stations")
def stations():
    # Return a JSON list of stations from the dataset
    session = Session(engine)
    station_count = session.query(Station.name).count() 
    stations = session.query(Station.id, Station.station, Station.name).all()
    session.close()

    station_list = []
    for row in stations:
        station_dict = {}
        station_dict["ID"]= row[0]
        station_dict["Station"]= row[1]
        station_dict["Name"] = row[2]
        station_list.append(station_dict)
    
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def temps():
    session = Session(engine)

    # Find most recent date
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    strdate = str(most_recent_date[0])
    # Calculate the date 1 year ago from the last data point in the database
    start_date = dt.datetime.strptime(strdate, "%Y-%m-%d") - dt.timedelta(days=366)

    #Query the dates and temperature observations of the most active station for the last year of data.
    most_active_station = 'USC00519281'
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.station == most_active_station).all()
    session.close()

    tobs_list = []
    for i in results:
        tobs_dict = {}
        tobs_dict["Date"] = i[0]
        tobs_dict["Temporature"] = i[1]
        tobs_list.append(tobs_dict)

    #Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def temp_stats1(start):
    # Return a JSON list of min, avg, and max temps for all dates greater than and equal to start date provided
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()    
    session.close()

    stats_list = []
    for i in results:
        stats_dict = {}
        stats_dict["Minimum"] = i[0]
        stats_dict["Average"] = i[1]
        stats_dict["Maximum"] = i[2]
        stats_list.append(stats_dict)
    
    return jsonify(stats_list)

@app.route("/api/v1.0/<start>/<end>")
    # Return a JSON list of min, avg, and max temps for all dates between dates provided, inclusive
def x(start,end):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date <= end).\
        filter(Measurement.date >= start).all()    
    session.close()

    stats_list = []
    for i in results:
        stats_dict = {}
        stats_dict["Minimum"] = i[0]
        stats_dict["Average"] = i[1]
        stats_dict["Maximum"] = i[2]
        stats_list.append(stats_dict)
    
    return jsonify(stats_list)

if __name__ == '__main__':
    app.run(debug=True)
