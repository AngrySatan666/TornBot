import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc
from datetime import datetime

# Connect to the database and load data
def load_data(db_path):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT timestamp, high, low FROM points_market ORDER BY timestamp ASC", conn)
    conn.close()
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def resample_to_ohlc(df):
    # Set timestamp as index
    df = df.set_index('timestamp')
    # Resample to 1-minute intervals
    ohlc = df['high'].resample('1T').ohlc()
    ohlc['low'] = df['low'].resample('1T').min()
    ohlc = ohlc.dropna()
    # For candlestick: [date, open, high, low, close]
    ohlc.reset_index(inplace=True)
    ohlc['date'] = ohlc['timestamp'].map(mdates.date2num)
    return ohlc[['date', 'open', 'high', 'low', 'close']]

def plot_candlestick(ohlc):
    fig, ax = plt.subplots(figsize=(12,6))
    candlestick_ohlc(ax, ohlc.values, width=0.02, colorup='g', colordown='r')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.title('Points Market High/Low Candlestick Chart (1min)')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def main():
    db_path = 'points.db'
    df = load_data(db_path)
    if df.empty:
        print('No data found in points.db')
        return
    ohlc = resample_to_ohlc(df)
    if ohlc.empty:
        print('No 1-minute intervals with data.')
        return
    plot_candlestick(ohlc)

if __name__ == '__main__':
    main()
