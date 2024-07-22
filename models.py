from extensions import db
from sqlalchemy.sql import func
from datetime import datetime
import pytz

def utc_to_ist(utc_dt):
    ist = pytz.timezone('Asia/Kolkata')
    utc = pytz.timezone('UTC')
    utc_dt = utc.localize(utc_dt)
    ist_dt = utc_dt.astimezone(ist)
    return ist_dt

class Share(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def created_at_ist(self):
        return utc_to_ist(self.created_at)

class StockData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    script = db.Column(db.String(80), nullable=False)
    concat = db.Column(db.String(50))
    mhb = db.Column(db.String(3))
    yhb = db.Column(db.String(3))
    percentage = db.Column(db.Float)
    high_to_high = db.Column(db.Float)
    price = db.Column(db.Float)
    ath = db.Column(db.Float)
    month_high = db.Column(db.Float)
    crossed_prior_month_high = db.Column(db.Boolean, default=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def last_updated_ist(self):
        return utc_to_ist(self.last_updated)