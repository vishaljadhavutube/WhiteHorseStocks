# stock_data.py
import yfinance as yf
from models import StockData
from extensions import db
from datetime import datetime, timedelta
import calendar

def get_max_high(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    if not data.empty:
        max_high = data['High'].max()
        return max_high
    else:
        return None

def get_current_price(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d")
    if not data.empty:
        current_price = data['Close'].iloc[-1]
        return current_price
    else:
        return None

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
    for ticker in share_list:
        share_name = ticker.split('.')[0]

        last_date_next_month = get_last_date_next_month()
        max_high_1980_to_next_month = get_max_high(ticker, "1980-01-01", last_date_next_month.strftime("%Y-%m-%d"))

        current_price = get_current_price(ticker)
        if current_price is not None:
            last_date_previous_year = get_last_date_previous_year()
            max_high_1980_to_last_year = get_max_high(ticker, "1980-01-01", last_date_previous_year.strftime("%Y-%m-%d"))

            previous_month_start, previous_month_end = get_previous_month_date_range()
            max_high_previous_month = get_max_high(ticker, previous_month_start.strftime("%Y-%m-%d"), previous_month_end.strftime("%Y-%m-%d"))

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
                existing_stock.percentage = all_time_high_percentage
                existing_stock.high_to_high = round(current_price - max_high_1980_to_last_year, 2) if max_high_1980_to_last_year else None
                existing_stock.price = round(current_price, 2)
                existing_stock.ath = round(max_high_1980_to_next_month, 2) if max_high_1980_to_next_month else None
                existing_stock.month_high = round(max_high_previous_month, 2) if max_high_previous_month else None
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
                    percentage=all_time_high_percentage,
                    high_to_high=round(current_price - max_high_1980_to_last_year, 2) if max_high_1980_to_last_year else None,
                    price=round(current_price, 2),
                    ath=round(max_high_1980_to_next_month, 2) if max_high_1980_to_next_month else None,
                    month_high=round(max_high_previous_month, 2) if max_high_previous_month else None,
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
