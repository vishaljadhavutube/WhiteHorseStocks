from extensions import db

class Share(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), unique=True, nullable=False)

class StockData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    script = db.Column(db.String(10), nullable=False)
    concat = db.Column(db.String(50))
    mhb = db.Column(db.String(3))
    yhb = db.Column(db.String(3))
    percentage = db.Column(db.Float)
    high_to_high = db.Column(db.Float)
    price = db.Column(db.Float)
    ath = db.Column(db.Float)
    month_high = db.Column(db.Float)
