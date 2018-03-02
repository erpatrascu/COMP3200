from app import db


class Zipcode(db.Model):
    __tablename__ = 'zipcode'

    zipcode = db.Column(db.Integer(), primary_key = True)
    density = db.Column(db.Float())
    wealthy = db.Column(db.Float())
    population = db.Column(db.Float())
    land_area = db.Column(db.Float())
    dist_to_south = db.Column(db.Float())
    dist_to_centre = db.Column(db.Float())

    def __init__(self, zipcode, density, wealthy, population, land_area, dist_to_south, dist_to_centre):
        self.zipcode = zipcode
        self.density = density
        self.wealthy = wealthy
        self.population = population
        self.land_area = land_area
        self.dist_to_south = dist_to_south
        self.dist_to_centre = dist_to_centre


class Weather(db.Model):
    __tablename__ = 'weather'

    #id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(), primary_key = True)
    avg_wind = db.Column(db.Float())
    tmax = db.Column(db.Float())
    tmin = db.Column(db.Float())
    tavg = db.Column(db.Float())
    precip = db.Column(db.Float())

    def __init__(self, date, avg_wind, tmax, tmin, tavg, precip):
        self.date = date
        self.avg_wind = avg_wind
        self.tmax = tmax
        self.tmin = tmin
        self.tavg = tavg
        self.precip = precip

class CrimeData(db.Model):
    __tablename__ = 'crime_data'

    id = db.Column(db.Integer, primary_key=True)
    zipcode = db.Column(db.Integer(), db.ForeignKey('zipcode.zipcode'))
    date = db.Column(db.DateTime(), db.ForeignKey('weather.date'))
    time = db.Column(db.Integer())
    weekday = db.Column(db.Integer())   #or string?
    month = db.Column(db.Integer())
    robberies_prev_month = db.Column(db.Float())
    robberies_6months = db.Column(db.Float())
    robberies_6months_time = db.Column(db.Float())
    robberies_2years_time = db.Column(db.Float())

    def __init__(self, zipcode, date,  time, weekday, month, robberies_prev_month, robberies_6months, robberies_6months_time, robberies_2years_time):
        self.zipcode = zipcode
        self.date = date
        self.time = time
        self.weekday = weekday
        self.month = month
        self.robberies_prev_month = robberies_prev_month
        self.robberies_6months = robberies_6months
        self.robberies_6months_time = robberies_6months_time
        self.robberies_2years_time = robberies_2years_time
