from app import db

#data about zipcodes
class Zipcode(db.Model):
    __tablename__ = 'zipcode'

    zipcode = db.Column(db.Integer(), primary_key = True)
    density = db.Column(db.Float())
    population = db.Column(db.Float())
    land_area = db.Column(db.Float())
    wealthy = db.Column(db.Float())
    total_wages = db.Column(db.Float())
    house_of_units = db.Column(db.Float())
    dist_to_south = db.Column(db.Float())
    dist_to_centre = db.Column(db.Float())
    boundary = db.Column(db.String())

    def __init__(self, zipcode, density, population, land_area, wealthy, total_wages, house_of_units, dist_to_south, dist_to_centre, boundary):
        self.zipcode = zipcode
        self.density = density
        self.population = population
        self.land_area = land_area
        self.wealthy = wealthy
        self.total_wages = total_wages
        self.house_of_units = house_of_units
        self.dist_to_south = dist_to_south
        self.dist_to_centre = dist_to_centre
        self.boundary = boundary


#weather data
class Weather(db.Model):
    __tablename__ = 'weather'

    date = db.Column(db.DateTime(), primary_key = True)
    tmax = db.Column(db.Float())
    tmin = db.Column(db.Float())

    def __init__(self, date, tmax, tmin):
        self.date = date
        self.tmax = tmax
        self.tmin = tmin


class CrimeType(db.Model):
    __tablename__ = 'crime_type'

    id = db.Column(db.Integer, primary_key = True)
    crimeType = db.Column(db.String())

    def __init__(self, crimeType):
        self.crimeType = crimeType


#crime statistics data
class CrimeData(db.Model):
    __tablename__ = 'crime_data'

    id = db.Column(db.Integer, primary_key=True)
    zipcode = db.Column(db.Integer(), db.ForeignKey('zipcode.zipcode'))
    year_month = db.Column(db.Integer())
    time = db.Column(db.Integer())
    count_1m_loc = db.Column(db.Float())
    count_6m_loc  = db.Column(db.Float())
    count_2y_loc  = db.Column(db.Float())
    count_1m_loc_time  = db.Column(db.Float())
    count_6m_loc_time = db.Column(db.Float())
    count_2y_loc_time = db.Column(db.Float())
    count_1m_time = db.Column(db.Float())
    count_6m_time = db.Column(db.Float())
    count_2y_time = db.Column(db.Float())
    crimes_per_pop = db.Column(db.Float())
    crime_type = db.Column(db.Integer(), db.ForeignKey('crime_type.id'))

    def __init__(self, zipcode, year_month,  time, count_1m_loc, count_6m_loc, count_2y_loc, 
                 count_1m_loc_time, count_6m_loc_time, count_2y_loc_time, count_1m_time,
                 count_6m_time, count_2y_time, crimes_per_pop, crime_type):
        self.zipcode = zipcode
        self.year_month = year_month
        self.time = time
        self.count_1m_loc = count_1m_loc
        self.count_6m_loc = count_6m_loc
        self.count_2y_loc = count_2y_loc
        self.count_1m_loc_time = count_1m_loc_time
        self.count_6m_loc_time = count_6m_loc_time
        self.count_2y_loc_time = count_2y_loc_time
        self.count_1m_time = count_1m_time
        self.count_6m_time = count_6m_time
        self.count_2y_time = count_2y_time
        self.crimes_per_pop = crimes_per_pop
        self.crime_type = crime_type
