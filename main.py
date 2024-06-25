import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import calendar


# Function to get the max high price within a given date range
def get_max_high(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    if not data.empty:
        max_high = data['High'].max()
        return max_high
    else:
        return None


# Function to get the current price
def get_current_price(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d")
    if not data.empty:
        current_price = data['Close'].iloc[-1]
        return current_price
    else:
        return None


# Function to get the last date of the previous year
def get_last_date_previous_year():
    today = datetime.today()
    last_date_previous_year = datetime(today.year - 1, 12, 31)
    return last_date_previous_year


# Function to get the start and end dates of the previous month
def get_previous_month_date_range():
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    first_day_of_previous_month = last_day_of_previous_month.replace(day=1)
    return first_day_of_previous_month, last_day_of_previous_month


# Function to get the last date of the next month
def get_last_date_next_month():
    today = datetime.today()
    next_month = today.month % 12 + 1
    next_month_year = today.year + (today.month // 12)
    last_day_next_month = calendar.monthrange(next_month_year, next_month)[1]
    last_date_next_month = datetime(next_month_year, next_month, last_day_next_month)
    return last_date_next_month


# Function to generate data for multiple shares and save to CSV
def generate_csv_for_shares(share_list):
    all_data = []

    for ticker in share_list:
        share_name = ticker.split('.')[0]

        # Get max high from 1980 to the last date of the next month
        last_date_next_month = get_last_date_next_month()
        max_high_1980_to_next_month = get_max_high(ticker, "1980-01-01", last_date_next_month.strftime("%Y-%m-%d"))
        print(
            f"Max high from 1980 to {last_date_next_month.strftime('%Y-%m-%d')} for {share_name}: {max_high_1980_to_next_month}")

        # Get current price
        current_price = get_current_price(ticker)
        if current_price is not None:
            print(f"Current price for {share_name}: {current_price}")

            # Get max high from 1980 to the last date of the previous year
            last_date_previous_year = get_last_date_previous_year()
            max_high_1980_to_last_year = get_max_high(ticker, "1980-01-01",
                                                      last_date_previous_year.strftime("%Y-%m-%d"))
            print(
                f"Max high from 1980 to {last_date_previous_year.year} for {share_name}: {max_high_1980_to_last_year}")

            # Get max high for the previous month
            previous_month_start, previous_month_end = get_previous_month_date_range()
            max_high_previous_month = get_max_high(ticker, previous_month_start.strftime("%Y-%m-%d"),
                                                   previous_month_end.strftime("%Y-%m-%d"))
            print(f"Max high for {previous_month_start.strftime('%B %Y')} for {share_name}: {max_high_previous_month}")

            # GET MONTHLY HIGH CONDITION
            if max_high_previous_month is not None and current_price > max_high_previous_month:
                print(f"{share_name}: MHB")
                month_high = "MHB"
            else:
                month_high = ""
                print(f"{share_name}: .")

            # GET YEARLY HIGH CONDITION
            if max_high_1980_to_last_year is not None and current_price > max_high_1980_to_last_year:
                print(f"{share_name}: YHB")
                year_high = "YHB"
            else:
                year_high = ""

            # GET ALL TIME HIGH IN PERCENTAGE
            if max_high_1980_to_next_month is not None:
                all_time_high_percentage = (current_price / max_high_1980_to_next_month) * 100
                all_time_high_percentage = round(all_time_high_percentage, 2)  # Round to 2 decimal places
                print(f"All time high percentage for {share_name}: {all_time_high_percentage:.2f}%")

            # Append data to list
            all_data.append({
                "SCRIPT": share_name,
                "CONCAT": f"{share_name},",
                "MHB": month_high,
                "YHB": year_high,
                "PERCENTAGE": all_time_high_percentage if max_high_1980_to_next_month is not None else None,
                "HIGH_TO_HIGH": round(current_price - max_high_1980_to_last_year,
                                      2) if max_high_1980_to_last_year is not None else None,
                "PRICE": round(current_price, 2),
                "ATH": round(max_high_1980_to_next_month, 2) if max_high_1980_to_next_month is not None else None,
                "MONTH_HIGH": round(max_high_previous_month, 2) if max_high_previous_month is not None else None
            })
        else:
            print(f"Failed to retrieve the current price for {share_name}.")

    # Create DataFrame
    df = pd.DataFrame(all_data)

    # Save to CSV
    df.to_csv("share_data.csv", index=False, float_format='%.2f')  # Set float_format to 2 decimal places
    print("Data saved to share_data.csv")


if __name__ == '__main__':
    # Example list of shares
    share_list = ["OFSS.NS", "TCS.NS", "INFY.NS"]

    # Generate CSV for the list of shares
    generate_csv_for_shares(share_list)
