# stock_data.py

import yfinance as yf
from models import StockData
from extensions import db
from datetime import datetime, timedelta
import calendar
import numpy as np

# def get_max_high(ticker, start_date, end_date):
#     data = yf.download(ticker, start=start_date, end=end_date)
#     if not data.empty:
#         max_high = data['High'].max()
#         return max_high
#     else:
#         return None

# def get_current_price(ticker):
#     stock = yf.Ticker(ticker)
#     data = stock.history(period="1d")
#     if not data.empty:
#         current_price = data['Close'].iloc[-1]
#         return current_price
#     else:
#         return None

import yfinance as yf
from datetime import datetime, timedelta
import calendar
import numpy as np
from models import StockData
from extensions import db
import pandas as pd

def get_max_high_batch(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date, group_by='ticker')
    max_highs = {}
    if isinstance(data.columns, pd.MultiIndex):
        for ticker in tickers:
            ticker_data = data[ticker]
            if not ticker_data.empty:
                max_highs[ticker] = ticker_data['High'].max()
            else:
                max_highs[ticker] = None
    else:
        if not data.empty:
            max_highs[tickers] = data['High'].max()
        else:
            max_highs[tickers] = None
    return max_highs

def get_current_price_batch(tickers):
    data = yf.download(tickers, period="1d", group_by='ticker')
    current_prices = {}
    if isinstance(data.columns, pd.MultiIndex):
        for ticker in tickers:
            ticker_data = data[ticker]
            if not ticker_data.empty:
                current_prices[ticker] = ticker_data['Close'].iloc[-1]
            else:
                current_prices[ticker] = None
    else:
        if not data.empty:
            current_prices[tickers] = data['Close'].iloc[-1]
        else:
            current_prices[tickers] = None
    return current_prices


def get_last_date_previous_year():
    today = datetime.today()
    last_date_previous_year = datetime(today.year - 1, 12, 31)
    return last_date_previous_year

def get_previous_month_date_range():
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    first_day_of_previous_month = last_day_of_previous_month.replace(day=1)
    return first_day_of_previous_month, last_day_of_previous_month

def get_last_date_next_month():
    today = datetime.today()
    next_month = today.month % 12 + 1
    next_month_year = today.year + (today.month // 12)
    last_day_next_month = calendar.monthrange(next_month_year, next_month)[1]
    last_date_next_month = datetime(next_month_year, next_month, last_day_next_month)
    return last_date_next_month
def update_stock_data(share_list):
    updated_stocks = []
    share_names = [ticker.split('.')[0] for ticker in share_list]

    last_date_next_month = get_last_date_next_month().strftime("%Y-%m-%d")
    max_highs_1980_to_next_month = get_max_high_batch(share_list, "1980-01-01", last_date_next_month)

    current_prices = get_current_price_batch(share_list)

    last_date_previous_year = get_last_date_previous_year().strftime("%Y-%m-%d")
    max_highs_1980_to_last_year = get_max_high_batch(share_list, "1980-01-01", last_date_previous_year)

    previous_month_start, previous_month_end = get_previous_month_date_range()
    previous_month_start = previous_month_start.strftime("%Y-%m-%d")
    previous_month_end = previous_month_end.strftime("%Y-%m-%d")
    max_highs_previous_month = get_max_high_batch(share_list, previous_month_start, previous_month_end)

    for ticker in share_list:
        share_name = ticker.split('.')[0]
        current_price = current_prices.get(ticker)
        if current_price is not None:
            max_high_1980_to_next_month = max_highs_1980_to_next_month.get(ticker)
            max_high_1980_to_last_year = max_highs_1980_to_last_year.get(ticker)
            max_high_previous_month = max_highs_previous_month.get(ticker)

            month_high = "MHB" if max_high_previous_month and current_price > max_high_previous_month else ""
            year_high = "YHB" if max_high_1980_to_last_year and current_price > max_high_1980_to_last_year else ""

            all_time_high_percentage = (current_price / max_high_1980_to_next_month) * 100 if max_high_1980_to_next_month else None
            all_time_high_percentage = round(all_time_high_percentage, 2) if all_time_high_percentage else None

            crossed_prior_month_high = current_price > max_high_previous_month if max_high_previous_month else False

            existing_stock = StockData.query.filter_by(script=share_name).first()
            if existing_stock:
                should_alert = False
                if month_high and not existing_stock.mhb:
                    existing_stock.mhb = month_high
                    should_alert = True
                if year_high and not existing_stock.yhb:
                    existing_stock.yhb = year_high
                    should_alert = True

                existing_stock.concat = f"{share_name},"
                existing_stock.percentage = float(all_time_high_percentage) if all_time_high_percentage is not None else None
                existing_stock.high_to_high = round(float(current_price) - float(max_high_1980_to_last_year), 2) if max_high_1980_to_last_year else None
                existing_stock.price = round(float(current_price), 2)
                existing_stock.ath = round(float(max_high_1980_to_next_month), 2) if max_high_1980_to_next_month else None
                existing_stock.month_high = round(float(max_high_previous_month), 2) if max_high_previous_month else None
                existing_stock.crossed_prior_month_high = crossed_prior_month_high

                if should_alert:
                    updated_stocks.append({
                        'script': existing_stock.script,
                        'mhb': existing_stock.mhb,
                        'yhb': existing_stock.yhb
                    })
            else:
                new_stock = StockData(
                    script=share_name,
                    concat=f"{share_name},",
                    mhb=month_high,
                    yhb=year_high,
                    percentage=float(all_time_high_percentage) if all_time_high_percentage is not None else None,
                    high_to_high=round(float(current_price) - float(max_high_1980_to_last_year), 2) if max_high_1980_to_last_year else None,
                    price=round(float(current_price), 2),
                    ath=round(float(max_high_1980_to_next_month), 2) if max_high_1980_to_next_month else None,
                    month_high=round(float(max_high_previous_month), 2) if max_high_previous_month else None,
                    crossed_prior_month_high=crossed_prior_month_high
                )
                db.session.add(new_stock)
                if month_high or year_high:
                    updated_stocks.append({
                        'script': new_stock.script,
                        'mhb': new_stock.mhb,
                        'yhb': new_stock.yhb
                    })
    db.session.commit()
    return updated_stocks