from flask import Flask, render_template, redirect, url_for, flash, request
from extensions import db
from forms import ShareForm
from stock_data import update_stock_data

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shares.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

from models import Share, StockData

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
    updated_stocks = update_stock_data([share.ticker for share in shares])

    if updated_stocks:
        return render_template('alert.html', updated_stocks=updated_stocks)

    flash('Stock data updated!', 'success')
    return redirect(url_for('view_data'))

@app.route('/view_data', methods=['GET', 'POST'])
def view_data():
    if request.method == 'POST':
        update_stock_data([share.ticker for share in Share.query.all()])
        flash('Stock data updated!', 'success')

    search = request.args.get('search')
    sort_by = request.args.get('sort_by', 'script')
    order = request.args.get('order', 'asc')

    query = StockData.query
    if search:
        query = query.filter(StockData.script.like(f'%{search}%'))

    stock_data = query.order_by(getattr(getattr(StockData, sort_by), order)()).all()

    return render_template('view_data.html', stock_data=stock_data)

if __name__ == '__main__':
    app.run(debug=True)
