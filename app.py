from flask import Flask, render_template, redirect, url_for, flash, request
from extensions import db
from forms import ShareForm
from stock_data import update_stock_data
from flask_migrate import Migrate

from models import Share, StockData

import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'postgresql://db_owner:vnSjPYcR5xL7@ep-plain-voice-a5jba9bq.us-east-2.aws.neon.tech/db?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)


@app.route('/')
def index():
    shares = Share.query.all()
    return render_template('index.html', shares=shares)


@app.route('/add_share', methods=['GET', 'POST'])
def add_share():
    form = ShareForm()
    if form.validate_on_submit():
        tickers = form.tickers.data
        ticker_list = [ticker.strip() for ticker in tickers.split(',')]
        added_tickers = []
        existing_tickers = []
        for ticker in ticker_list:
            if not Share.query.filter_by(ticker=ticker).first():
                new_share = Share(ticker=ticker)
                db.session.add(new_share)
                added_tickers.append(ticker)
            else:
                existing_tickers.append(ticker)
        db.session.commit()
        if added_tickers:
            flash(f'Shares {", ".join(added_tickers)} added!', 'success')
        if existing_tickers:
            flash(f'Shares {", ".join(existing_tickers)} already exist.', 'warning')
        return redirect(url_for('index'))
    return render_template('add_share.html', form=form)


@app.route('/delete_share/<int:share_id>', methods=['POST'])
def delete_share(share_id):
    share = Share.query.get_or_404(share_id)
    stock_data_entries = StockData.query.filter_by(script=share.ticker.split('.')[0]).all()
    for entry in stock_data_entries:
        db.session.delete(entry)
    db.session.delete(share)
    db.session.commit()
    flash(f'Share {share.ticker} and its associated data deleted!', 'success')
    return redirect(url_for('index'))


@app.route('/update_data')
def update_data():
    shares = Share.query.all()
    tickers = [share.ticker for share in shares]
    updated_stocks = update_stock_data(tickers)
    if updated_stocks:
        return render_template('alert.html', updated_stocks=updated_stocks)
    flash('Stock data updated!', 'success')
    return redirect(url_for('index'))


@app.route('/view_data', methods=['GET', 'POST'])
def view_data():
    if request.args.get('refresh') == 'true':
        updated_stocks = update_stock_data([share.ticker for share in Share.query.all()])
        if updated_stocks:
            flash('Stock data updated!', 'success')

    search = request.args.get('search')
    sort_by = request.args.get('sort_by', 'script')
    order = request.args.get('order', 'asc')

    query = StockData.query
    if search:
        query = query.filter(StockData.script.like(f'%{search}%'))

    if order == 'desc':
        stock_data = query.order_by(getattr(StockData, sort_by).desc()).all()
    else:
        stock_data = query.order_by(getattr(StockData, sort_by).asc()).all()

    return render_template('view_data.html', stock_data=stock_data)
@app.route('/alert')
def alert():
    updated_stocks = request.args.get('updated_stocks')
    return render_template('alert.html', updated_stocks=updated_stocks)


if __name__ == '__main__':
    app.run(debug=True)
