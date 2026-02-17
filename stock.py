import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import seaborn as sb
import yfinance as yf

sb.set_theme()

"""
STUDENT CHANGE LOG & AI DISCLOSURE:
----------------------------------
1. Did you use an LLM (ChatGPT/Claude/etc.)? Yes
2. Primary prompt: "Help me implement get_data, calc_returns, technical indicators, and plotting
   methods for the Stock class using yfinance, pandas, numpy, and matplotlib."
----------------------------------
"""

DEFAULT_START = dt.date.isoformat(dt.date.today() - dt.timedelta(365))
DEFAULT_END = dt.date.isoformat(dt.date.today())




class Stock:
    def __init__(self, symbol, start=DEFAULT_START, end=DEFAULT_END):
        self.symbol = symbol
        self.start = start
        self.end = end
        self.data = self.get_data()

    def get_data(self):
        """Downloads data from yfinance and triggers return calculation."""
        data = yf.download(self.symbol, start=self.start, end=self.end, progress=False)

        if data is None or data.empty:
            raise ValueError(f"No data returned for symbol '{self.symbol}'")

        # ensure datetime index
        data.index = pd.to_datetime(data.index)
        data.index.name = "Date"

        # add return columns
        data = self.calc_returns(data)

        return data

    def calc_returns(self, df):
        """Adds 'change' and 'instant_return' columns to the dataframe."""
        df["change"] = df["Close"].diff()
        df["instant_return"] = np.log(df["Close"]).diff().round(4)
        return df

    def add_technical_indicators(self, windows=[20, 50]):
        """
        Add Simple Moving Averages (SMA) for the given windows
        to the internal DataFrame. Produce a plot showing the closing price and SMAs.
        """
        df = self.data

        for w in windows:
            df[f"SMA_{w}"] = df["Close"].rolling(window=w).mean()

        plt.figure(figsize=(11, 5))
        plt.plot(df.index, df["Close"], label="Close")

        for w in windows:
            plt.plot(df.index, df[f"SMA_{w}"], label=f"SMA {w}")

        plt.title(f"{self.symbol} Closing Price + SMAs")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

    def plot_return_dist(self, bins=40):
        """Plot histogram of instantaneous returns."""
        df = self.data
        returns = df["instant_return"].dropna()

        plt.figure(figsize=(10, 5))
        plt.hist(returns, bins=bins, edgecolor="black")
        plt.title(f"{self.symbol} Instantaneous Return Distribution")
        plt.xlabel("Instantaneous Return (log)")
        plt.ylabel("Frequency")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

    def plot_performance(self):
        """Plots cumulative growth of $1 investment."""
        df = self.data

        start_price = df["Close"].iloc[0]
        performance = df["Close"] / start_price  # value of $1 invested

        plt.figure(figsize=(11, 5))
        plt.plot(df.index, performance)
        plt.title(f"{self.symbol} Growth of $1 Investment")
        plt.xlabel("Date")
        plt.ylabel("Value ($)")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()


def main():
    aapl = Stock("AAPL")

    # Access the data attribute (required)
    print(aapl.data.head())

    # Generate the two required plots
    aapl.plot_return_dist()
    aapl.plot_performance()

    # Add technical indicators + plot
    aapl.add_technical_indicators()


if __name__ == "__main__":
    main()
