#!/usr/bin/env python3

import pandas as pd
import requests
from datetime import datetime, timedelta
import numpy as np
from syncData import syncData

#%%

test = ""
# test = "-test"

cols = ['row', 'lga', 'state', 'date', 'cases']

print("Getting data..")

json = requests.get('https://interactive.guim.co.uk/covidfeeds/victoria-export.json').json()

#%%

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ9oKYNQhJ6v85dQ9qsybfMfc-eaJ9oKVDZKx-VGUr6szNoTbvsLTzpEaJ3oW_LZTklZbz70hDBUt-d/pub?gid=0&single=true&output=csv"
print("Getting", url)
r = requests.get(url)
with open("vic-latest.csv", 'w') as f:
	f.write(r.text)

#%%

latest = pd.read_csv('vic-latest.csv)


#%%

df = pd.DataFrame(json)

df.columns = cols
df.date = pd.to_datetime(df.date, format="%Y-%m-%d")
df = df.set_index('date')
df = df.sort_index(ascending=1)
df['cases'] = pd.to_numeric(df['cases'])

lastUpdated = df.index[-1]
one_month_ago = lastUpdated - timedelta(days=30)

current_df = df[df.index == lastUpdated].reset_index().set_index('lga')

#%%
one_month_df = df[df.index == one_month_ago].reset_index().set_index('lga')

current_df['one_month_ago'] = one_month_df['cases']


#%%

short = df[one_month_ago:]

short_p = short.pivot(columns='lga', values='cases')

short_p.to_csv('cases_lga.csv')

lga_daily = pd.DataFrame()

for col in short_p.columns:
	tempSeries = short_p[col].dropna()
	tempSeries = tempSeries.sub(tempSeries.shift())
# 	tempSeries.iloc[0] = short_p[col].dropna().iloc[0]
	lga_daily = pd.concat([lga_daily, tempSeries], axis=1)

# lga_daily = lga_daily[:-2]

last_row = lga_daily[-1:].squeeze()
allZeroes = True
for index, value in last_row.items():
	if value != 0:
		allZeroes = False
		break
if allZeroes:
	lga_daily = lga_daily[:-1]

two_weeks_ago = lga_daily.index[-1] - timedelta(days=13)

totals = lga_daily[two_weeks_ago:].sum()

totals_30day = lga_daily[one_month_ago:].sum().to_frame('count').reset_index()
totals_30day = totals_30day.rename(columns={"index":'place'})

totals_30day['date'] = lastUpdated.strftime('%Y-%m-%d')

totals_30day['count'][totals_30day['count'] < 0] = 0

totals = totals[totals >= 5]

lga_daily.to_csv('lga_daily.csv')

one_week_ago = lga_daily.index[-1] - timedelta(days=6)

blah = totals_30day.to_dict(orient='records')

#%%

no_negs = lga_daily

no_negs[no_negs < 0] = 0

rolling = no_negs.rolling(7).mean()
rolling.to_csv("rolling.csv")
lga_movement = []

for col in totals.index:
	print(col)
	row = {}
	row['lga'] = col
	row['change'] = rolling.loc[lga_daily.index[-1], col] - rolling.loc[one_week_ago, col]
	row['this_week'] = lga_daily[one_week_ago:][col].sum()
	row['last_week'] = lga_daily[two_weeks_ago:one_week_ago - timedelta(days=1)][col].sum()
	row['weekly_change'] = 	row['this_week'] - row['last_week']
	row['date'] = lga_daily.index[-1].strftime('%Y-%m-%d')
	lga_movement.append(row)

lga_df_movement1 = pd.DataFrame(lga_movement)


#%%

syncData(lga_movement,'2020/07/vic-corona-map{test}'.format(test=test), "vicChange-2")
	
syncData(totals_30day.to_dict(orient='records'),'2020/07/vic-corona-map{test}'.format(test=test), "vicTotals")

# short['rolling_mean'] = df.groupby('lga')['cases'].transform(lambda x: x.rolling(7, 1).mean())


