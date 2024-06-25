from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError
import yfinance as yf


class ShareForm(FlaskForm):
    tickers = StringField('Tickers (comma separated)', validators=[DataRequired()])
    submit = SubmitField('Add Shares')

    def validate_tickers(self, tickers):
        ticker_list = [ticker.strip() for ticker in tickers.data.split(',')]
        invalid_tickers = []
        for ticker in ticker_list:
            stock = yf.Ticker(ticker)
            try:
                if stock.history(period="1d").empty:
                    invalid_tickers.append(ticker)
            except Exception:
                invalid_tickers.append(ticker)
        if invalid_tickers:
            raise ValidationError(f'Invalid ticker symbols: {", ".join(invalid_tickers)}. Please enter valid tickers.')
