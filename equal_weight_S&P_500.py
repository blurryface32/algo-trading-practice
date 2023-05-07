#!/usr/bin/env python
# coding: utf-8

# # Equal-Weight S&P 500 Index Fund
# 
# ## Introduction & Library Imports
# 
# The S&P 500 is the world's most popular stock market index. The largest fund that is benchmarked to this index is the SPDR® S&P 500® ETF Trust. It has more than US$250 billion of assets under management.
# 
# The goal of this section of the course is to create a Python script that will accept the value of your portfolio and tell you how many shares of each S&P 500 constituent you should purchase to get an equal-weight version of the index fund.
# 
# ## Library Imports
# 
# The first thing we need to do is import the open-source software libraries that we'll be using in this tutorial.

# In[ ]:


import numpy as np
import pandas as pd
import math
import requests

import sys
get_ipython().system('{sys.executable} -m pip install xlsxwriter')


# ## Importing Our List of Stocks
# 
# The next thing we need to do is import the constituents of the S&P 500.
# 
# These constituents change over time, so in an ideal world you would connect directly to the index provider (Standard & Poor's) and pull their real-time constituents on a regular basis.
# 
# Paying for access to the index provider's API is outside of the scope of this course. 
# 
# There's a static version of the S&P 500 constituents available here. [Click this link to download them now](https://drive.google.com/file/d/1ZJSpbY69DVckVZlO9cC6KkgfSufybcHN/view?usp=sharing). Move this file into the `starter-files` folder so it can be accessed by other files in that directory.
# 
# Now it's time to import these stocks to our Jupyter Notebook file.

# In[158]:


stocks = pd.read_csv('sp_500_stocks.csv')
type(stocks)


# ## Acquiring an API Token
# 
# Now it's time to import our IEX Cloud API token. This is the data provider that we will be using throughout this course.
# 
# API tokens (and other sensitive information) should be stored in a `secrets.py` file that doesn't get pushed to your local Git repository. We'll be using a sandbox API token in this course, which means that the data we'll use is randomly-generated and (more importantly) has no cost associated with it.
# 
# [Click here](http://nickmccullum.com/algorithmic-trading-python/secrets.py) to download your `secrets.py` file. Move the file into the same directory as this Jupyter Notebook before proceeding.

# In[159]:


from secrets import IEX_CLOUD_API_TOKEN


# ## Making Our First API Call
# 
# Now it's time to structure our API calls to IEX cloud. 
# 
# We need the following information from the API:
# 
# * Market capitalization for each stock
# * Price of each stock
# 
# 

# In[235]:


symbol = 'AAPL'
api_url = f'https://api.iex.cloud/v1/data/core/quote/{symbol}?token=sk_30ba51ebaa3647d983ba079eb907bac8'
data = requests.get(api_url).json()
print(data[0])
data1=requests.get(api_url)


# ## Parsing Our API Call
# 
# The API call that we executed in the last code block contains all of the information required to build our equal-weight S&P 500 strategy. 
# 
# With that said, the data isn't in a proper format yet. We need to parse it first.

# In[231]:


price = data[0]['latestPrice']
market_cap = data[0]['marketCap']
print(price)


# ## Adding Our Stocks Data to a Pandas DataFrame
# 
# The next thing we need to do is add our stock's price and market capitalization to a pandas DataFrame. Think of a DataFrame like the Python version of a spreadsheet. It stores tabular data.

# In[163]:


my_columns = ['Ticker','Stock Price','Market Capitalization','No. of Shares to Buy']
final=pd.DataFrame(columns=my_columns)
final


# In[164]:


final.append(
    pd.Series(
    [
        symbol,
        price,
        market_cap,
        'N/A'
    ],
        index = my_columns
    ),
    
    ignore_index=True

)


# ## Looping Through The Tickers in Our List of Stocks
# 
# Using the same logic that we outlined above, we can pull data for all S&P 500 stocks and store their data in the DataFrame using a `for` loop.

# In[253]:


final=pd.DataFrame(columns=my_columns)
number=0
for stock in stocks['Ticker'][:5]:
    api_url = f'https://api.iex.cloud/v1/data/core/quote/{stock}?token=sk_30ba51ebaa3647d983ba079eb907bac8'
    data = requests.get(api_url).json()
    final=final.append(
        pd.Series(
        [
            stock,
            data[number]['latestPrice'],
            data[number]['marketCap'],
            'N/A'
        ],
        index=my_columns
        ),
        ignore_index=True
    )
  


# In[254]:


final


# ## Using Batch API Calls to Improve Performance
# 
# Batch API calls are one of the easiest ways to improve the performance of your code.
# 
# This is because HTTP requests are typically one of the slowest components of a script.
# 
# Also, API providers will often give you discounted rates for using batch API calls since they are easier for the API provider to respond to.
# 
# IEX Cloud limits their batch API calls to 100 tickers per request. Still, this reduces the number of API calls we'll make in this section from 500 to 5 - huge improvement! In this section, we'll split our list of stocks into groups of 100 and then make a batch API call for each group.

# In[167]:


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
        


# In[276]:


symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_groups
final=pd.DataFrame(columns=my_columns)
number=0
for stock in stocks['Ticker'][:4]:
    api_url = f'https://api.iex.cloud/v1/data/core/quote/{stock}?token=sk_30ba51ebaa3647d983ba079eb907bac8'
    data = requests.get(api_url).json()
    final=final.append(
        pd.Series(
        [
            stock,
            data[number]['latestPrice'],
            data[number]['marketCap'],
            'N/A'
        ],
        index=my_columns
        ),
        ignore_index=True
    )
print(final)
print(data[0])
print(data)


# In[362]:


symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings=[]
for i in range(0,len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
final=pd.DataFrame(columns=my_columns)
for symbol_string in symbol_strings:
    batch_api_call_url=f'https://apis.iex.cloud/v1/data/CORE/QUOTE/{symbol_string}?token=sk_30ba51ebaa3647d983ba079eb907bac8'
    n=0
    print(batch_api_call_url)
    data=requests.get(batch_api_call_url).json()
    #print(data[0])
    #print(data[1])
    for symbol in symbol_string.split(','):
        final = final.append(
            pd.Series(
                [
                    symbol,
                    data[n]['latestPrice'],
                    data[n]['marketCap'],
                    'N/A'
                ],
                index = my_columns),
                ignore_index = True
        )
        n=n+1
    
    
final
   #stock/market/batch?symbols=aapl,fb,tsla&types=quote,news,chart&range=1m&last=5'
    #/data/CORE/QUOTE.FUNDAMENTALS/SPY.MSFT?batchSeparator=.
 
      
    


# In[ ]:





# ## Calculating the Number of Shares to Buy
# 
# As you can see in the DataFrame above, we stil haven't calculated the number of shares of each stock to buy.
# 
# We'll do that next.

# In[381]:


portfolio_size=input('Enter the value of your portfolio: ')

try:
    val=float(portfolio_size)
except ValueError:
    print("That's not a number! \nPlease try again: ")
    portfolio_size=input('Enter the value of your portfolio: ')
    val=float(portfolio_size)


# ### Creating the Formats We'll Need For Our `.xlsx` File
# 
# Formats include colors, fonts, and also symbols like `%` and `$`. We'll need four main formats for our Excel document:
# * String format for tickers
# * \\$XX.XX format for stock prices
# * \\$XX,XXX format for market capitalization
# * Integer format for the number of shares to purchase

# In[382]:


position_size=val/len(final.index)
#print(position_size)

for i in range(0,len(final.index)):
    final.loc[i, 'No. of Shares to Buy'] = math.floor(position_size/final.loc[i,'Stock Price'])
final
print(final)


# ## Formatting Our Excel Output
# 
# We will be using the XlsxWriter library for Python to create nicely-formatted Excel files.
# 
# XlsxWriter is an excellent package and offers tons of customization. However, the tradeoff for this is that the library can seem very complicated to new users. Accordingly, this section will be fairly long because I want to do a good job of explaining how XlsxWriter works.
# 
# ### Initializing our XlsxWriter Object

# In[383]:


writer=pd.ExcelWriter('recommended_trades.xlsx',engine='xlsxwriter')
final.to_excel(writer,'Recommended Trades',index=False)


# In[384]:


background_color='#0a0a23'
font_color='ffffff'

string_format = writer.book.add_format(
    {
        'font_color':font_color,
        'bg_color':background_color,
        'border':1
    }
)

dollar_format = writer.book.add_format(
    {
        'num_format':'$0.00',
        'font_color':font_color,
        'bg_color':background_color,
        'border':1
    }
)

integer_format = writer.book.add_format(
    {
        'num_format':'0',
        'font_color':font_color,
        'bg_color':background_color,
        'border':1
    }
)


# ### Applying the Formats to the Columns of Our `.xlsx` File
# 
# We can use the `set_column` method applied to the `writer.sheets['Recommended Trades']` object to apply formats to specific columns of our spreadsheets.
# 
# Here's an example:
# 
# ```python
# writer.sheets['Recommended Trades'].set_column('B:B', #This tells the method to apply the format to column B
#                      18, #This tells the method to apply a column width of 18 pixels
#                      string_template #This applies the format 'string_template' to the column
#                     )
# ```

# In[385]:


#writer.sheets['Recommended Trades'].set_column('A:A',18,string_format)
#writer.sheets['Recommended Trades'].set_column('B:B',18,dollar_format)
#writer.sheets['Recommended Trades'].set_column('C:C',18,dollar_format)
#writer.sheets['Recommended Trades'].set_column('D:D',18,integer_format)
#writer.save()

#writer.sheets['Recommended Trades'].write('A1','Ticker',string_format)
#writer.sheets['Recommended Trades'].write('B1','Stock Price',dollar_format)
#writer.sheets['Recommended Trades'].write('C1','Market Capitalization',dollar_format)
#writer.sheets['Recommended Trades'].write('D1','No. of Shares to Buy',integer_format)


# This code works, but it violates the software principle of "Don't Repeat Yourself". 
# 
# Let's simplify this by putting it in 2 loops:

# In[386]:


column_formats={
    'A':['Ticker', string_format],
    'B':['Stock Price', dollar_format],
    'C':['Market Capitalization', dollar_format],
    'D':['Number of Shares to Buy',integer_format]
}
for column in column_formats.keys():
    writer.sheets['Recommended Trades'].set_column(f'{column}:{column}',18,column_formats[column][1])
    writer.sheets['Recommended Trades'].write(f'{column}1',column_formats[column][0],column_formats[column][1])


# ## Saving Our Excel Output
# 
# Saving our Excel file is very easy:

# In[387]:


writer.save()


# In[ ]:




