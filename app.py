import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
Stations = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def Homepage():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/?start<br/>"
        f"/api/v1.0/?start/?end<br/>"
    )


@app.route("/api/v1.0/precipitation")
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(measurement.date,measurement.prcp).\
    filter(measurement.date <= '2017-08-23').\
    filter(measurement.date >= '2016-08-23').\
    order_by(measurement.date).all()

    session.close()
    
    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results = session.query(Stations.station, Stations.name).all()

    session.close()

    all_stations = []
    for station, name in results:
        all_stations.append(station)

    return jsonify(all_stations)
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    most_active = session.query(measurement.station, func.count(measurement.station)).\
    group_by(measurement.station).\
    order_by(func.count(measurement.station).desc()).first()

    
    yearly_temps = session.query(measurement.date,measurement.tobs).\
    filter(measurement.date <= '2017-08-23').\
    filter(measurement.date >= '2016-08-23').\
    filter(measurement.station == most_active.station).\
    order_by(measurement.date).all()

    session.close()

    temps = []
    for date, temp in yearly_temps:
        temps.append(temp)

    return jsonify(temps)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def dates(start=None,end=None):
    session = Session(engine)
    if end==None:
        results = session.query((measurement.date),func.avg(measurement.tobs),func.min(measurement.tobs),func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()
    else:
        results = session.query((measurement.date),func.avg(measurement.tobs),func.min(measurement.tobs),func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date < end).all()
    
    session.close()

    allResults = []
    for date, ave, min, max in results:
        resultsDict = {}
        resultsDict['StartDate'] = start
        resultsDict['EndtDate'] = end
        resultsDict['TAve'] = ave
        resultsDict['TMin'] = min
        resultsDict['TMax'] = max

        allResults.append(resultsDict)
    return jsonify(allResults)
if __name__ == '__main__':
    app.run(debug=True)
