#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 13:20:34 2024

@author: simonlesflex
"""
apiToken = ''
chatID = ''
apiURL = f'https://api.telegram.org/bot{apiToken}/'


from flask import Flask, render_template, request
import yfinance as yf  # Assuming you have yfinance installed (pip install yfinance)
import pandas as pd
from TelegramMain import send_file, send_photo, send_to_telegram
from datetime import date, time, datetime, timedelta
import os
import matplotlib.pyplot as plt

G_SLICEDAYS = 252 * 2
G_FILEPREF = 'MomentumDashFactors_'
G_MAINTitle = 'Momentum Dashboard FACTORS'

UNIVERSE_CSV = 'MomDashboardUNIVERSE.csv'
G_MAINFolder = '/home/simonlesflex/PythonProjects/Dashboard'

FactorTick = ['XLF', 'XLRE', 'XLC', 'XLE', 'XLB', 'XLI', 'XLY', 'XLP', 'XLU', 'XLK', 'XLV']
#IntlTick = ['EEM', 'DBC', 'EWJ', 'FEZ']
#ROCTick = ['GLD', 'SLV', 'DBB']
#HighYieldTick = ['TECL', 'VTV', 'VUG', 'IJT']
HighYieldTick = ['VTV', 'VUG', 'IJT']
#BondTick = ['TLT', 'IEF', 'SHV', 'VUSTX', 'UUP']
#BondTick = ['TLT', 'IEF', 'VUSTX', 'UUP']

#TickerLIST = FactorTick + IntlTick + ROCTick + HighYieldTick + BondTick
TickerLIST = FactorTick + HighYieldTick
#TickerLIST = ROCTick

startdate = datetime(2008, 1, 1)
enddate = datetime.today()
#startdate = datetime(enddate.year - 5, 1, 1)

RefreshFlag = True
TelegramFLAG = True

os.chdir(G_MAINFolder)

# Define some helper functions to calculate momentum scores
def calculate_momentum(etf, timeframe):
  prices = yf.download(etf, period=f"{timeframe}d")["Close"]
  return (prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0] * 100

def calculate_antonacci_momentum(etf, timeframe):
  # Implement Antonacci's Momentum score calculation here (replace with your formula)
  # This example uses a simple moving average crossover strategy
  prices = yf.download(etf, period=f"{timeframe}d")["Close"]
  sma_50 = prices.rolling(window=50).mean()
  sma_200 = prices.rolling(window=200).mean()
  return (sma_50.iloc[-1] > sma_200.iloc[-1]) * 100  # 100 for long position, -100 for short

# Define available timeframes
timeframes = {
    #"10Days": 10,
    #"15Days": 15,
    #"20Days": 20,
    "30Days": 30,
    #"48Days": 48,
    "64Days": 64,
    "128Days": 128,
    "252Days": 252,
    "5Years": 252 * 5,
}

# Define a dictionary to store ETF data
etf_data = {}

DFAdjClose = pd.DataFrame()
if RefreshFlag is True:
    for ticker in TickerLIST:
        adj_close = []
        ticker_module = yf.Ticker(ticker)
        #data = yf.download(ticker, start=startdate, end=enddate, interval="1mo")
        data = yf.download(ticker, start=startdate, end=enddate, ignore_tz=True)
        adj_close = pd.DataFrame(columns=[f'{ticker}'])
        adj_close[ticker] = data['Close']
        low = data['Low']
        high = data['High']
        
        #adj_close.rename(f'{ticker}_Close', inplace=True)
        #adj_close.index = adj_close.index.tz_localize(None)
        for TF in timeframes:
            momDF = []
            momDF = adj_close[ticker].pct_change(timeframes[TF]) * 100
            momDF = momDF.rolling(5).mean()
            adj_close[ticker + TF] = momDF.bfill()

        DFAdjClose = pd.concat([DFAdjClose, adj_close], axis=1)
    
    
    # combine all dataframes into a single dataframe
    DFAdjClose.to_csv(UNIVERSE_CSV)

else:
    pass



def plot_timeframe_groups(dataframe, column_prefix, timeframes, slicedays):
  """
  This function groups DataFrame columns by timeframes and displays separate plots 
  for each timeframe, iterating through a list of ticker categories.

  Args:
      dataframe: The DataFrame containing the data.
      column_prefix: The prefix of the columns containing timeframe information 
                     (e.g., "GLD").
      timeframes: A dictionary mapping timeframe names to their corresponding number 
                  of days.
      ticker_lists: A list containing sub-lists of tickers categorized by group names 
                   (e.g., FactorTick, IntlTick).
  """

  # Select columns with matching prefixes
  #timeframe_cols = [col for col in dataframe.columns if col.find(column_prefix)]
  timeframe_cols = [col for col in dataframe.columns if column_prefix in col]

# Check if timeframe_cols is a DataFrame (assuming single row for selection)
  if isinstance(timeframe_cols, pd.DataFrame):
    timeframe_cols = timeframe_cols.iloc[0]  # Extract column names from first row

  # Select columns from df based on timeframe_cols
  selected_df = df[timeframe_cols][-slicedays:]
  
  plotTitle = G_MAINTitle + ' - TimeFrame: ' + str(column_prefix)

  # Plot the data
  ax = selected_df.plot(figsize=(24, 12), linewidth=2) 
  ax.set_xlabel("Date")
  ax.set_ylabel("Value")
  ax.set_title(plotTitle)
  ax.grid(True)  # Add grid lines
  ax.legend(title="Columns")  # Add legend for clarity
  plt.tight_layout()  # Improve layout

  # Customize line styles and colors (optional)
  lines = ax.get_lines()  # Get line objects
  # Set different line styles and colors for each line (example)
  for i, line in enumerate(lines):
    line.set_linestyle('-')
    #line.set_color(plt.cm.viridis(i / len(lines)))  # Set color using colormap
  filename = G_FILEPREF + column_prefix + '.png'
  plt.savefig(filename)
  plt.show()

  if TelegramFLAG:
      with open(filename, "rb") as fmomdash:
          send_file(chatID, fmomdash)


# Example usage
df = pd.DataFrame(DFAdjClose.copy())  # Assuming DFAdjClose is your actual DataFrame
#column_prefix = "GLD"  # Adjust this based on your column prefix
columnTF = "10Days"  # Adjust this based on your column prefix

#TickerLIST = ['XLF', 'XLRE', 'XLC', 'XLE', 'XLB', 'XLI', 'XLY', 'XLP', 'XLU', 'XLK', 'XLV', 'EEM', 'DBC', 'EWJ', 'FEZ', 'GLD', 'SLV', 'DBB', 'TECL', 'VTV', 'VUG', 'IJT', 'TLT', 'IEF', 'SHV', 'VUSTX', 'UUP']
ticker_lists = [[x for x in tickers if x in df.columns] for tickers in TickerLIST]
#plot_timeframe_groups(df, columnTF, timeframes)

for row in timeframes:
    columnTF = row
    plot_timeframe_groups(df, columnTF, timeframes, G_SLICEDAYS)
