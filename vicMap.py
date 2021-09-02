#!/usr/bin/env python3

import pandas as pd
import requests
from datetime import datetime, timedelta
import numpy as np
from syncData import syncData
from yachtCharter import yachtCharter


pd.options.mode.chained_assignment = None  # default='warn'

url = "https://www.dhhs.vic.gov.au/ncov-covid-cases-by-lga-source-csv"
print("Getting", url)
r = requests.get(url)
with open("vic-lga.csv", 'w') as f:
	f.write(r.text)

#%%

df = pd.read_csv("vic-lga.csv")
today = datetime.today().strftime('%-d %B, %Y')
#%%

df = df.rename(columns={"diagnosis_date": "date", "Localgovernmentarea": "lga" })
df.date = pd.to_datetime(df.date, format="%Y-%m-%d")

df = df.sort_values(['date'])

df['count'] = 1
local = df[df['acquired'] != "Travel overseas"]
local_gp = local[['date','lga','count']].groupby(['date','lga']).sum()
local_gp = local_gp.reset_index()
local_gp = local_gp.set_index('date')

lastUpdated = df['date'].iloc[-1]

four_weeks_ago = lastUpdated - timedelta(days=28)

thirty_days = lastUpdated - timedelta(days=30)

short = local_gp[thirty_days:]

short_p = short.pivot(columns='lga', values='count')

map_index = pd.date_range(start=thirty_days, end=lastUpdated)
short_p = short_p.reindex(map_index)

short_p.to_csv('lga-cases.csv')

two_weeks_ago = lastUpdated - timedelta(days=13)
one_week_ago = lastUpdated - timedelta(days=7)

totals = short_p[two_weeks_ago:].sum()

recent_totals = short_p.sum()

totals = totals[totals >= 5]

short_p.fillna(0, inplace=True)

no_negs = short_p

no_negs[short_p < 0] = 0

rolling = no_negs.rolling(7).mean()

rolling.to_csv("rolling.csv")
lga_movement = []

for col in totals.index:
	print(col)
	row = {}
	row['lga'] = col
	row['change'] = rolling.loc[lastUpdated, col] - rolling.loc[one_week_ago, col]
	row['this_week'] = short_p[one_week_ago:][col].sum()
	row['last_week'] = short_p[two_weeks_ago:one_week_ago][col].sum()
	row['weekly_change'] = 	row['this_week'] - row['last_week']
	row['date'] = short_p.index[-1].strftime('%Y-%m-%d')
	row['today'] = today
	lga_movement.append(row)

lga_df_movement1 = pd.DataFrame(lga_movement)

# lga_recent = []

recent_totals = recent_totals.reset_index().rename(columns={"lga": "place", 0: "count" })
recent_totals['date'] = short_p.index[-1].strftime('%Y-%m-%d')
recent_totals['today'] = today
recent_totals.to_json()

#%%

syncData(lga_movement,'2020/07/vic-corona-map', "vicChange-3")

syncData(recent_totals.to_dict('records'),'2020/07/vic-corona-map', "vicTotals")


#%%
long = local_gp["2021-06-10":]
long_p = long.pivot(columns='lga', values='count')
long_p.fillna(0, inplace=True)
long_p[short_p < 0] = 0
long_p_rolling = long_p.rolling(7).mean()

lga_totals = lga_df_movement1.copy()
lga_totals = lga_totals.sort_values(['this_week'], ascending=False)

long_p_rolling = long_p_rolling[list(lga_totals.lga)]

long_p_rolling.index = long_p_rolling.index.strftime('%Y-%m-%d')

long_stack = long_p_rolling.stack().reset_index().rename(columns={"level_1":"LGA", 0:"Trend in cases"})
long_stack = long_stack.set_index('date')	
long_stack = long_stack.round(2)

def makeLgaTrend(df):
	
	template = [
			{
				"title": "Trend in cases by LGA in the Victorian Covid outbreak",
				"subtitle": "Showing the seven-day rolling average in daily Covid cases for each LGA with five or more recent cases. Last updated {date}".format(date=today),
				"footnote": "",
				"source": " | Source: Guardian Australia analysis of Vic Department of Health data",
				"dateFormat": "%Y-%m-%d",
				"xAxisLabel": "",
				"yAxisLabel": "",
				"timeInterval":"day",
				"tooltip":"<b>{{#nicedate}}notification_date{{/nicedate}}</b><br><b>Cases, 7-day avg:</b> {{Trend in cases}}",
				"periodDateFormat":"",
				"margin-left": "27",
				"margin-top": "5",
				"margin-bottom": "22",
				"margin-right": "22",
				"xAxisDateFormat": "%b %d"
			}
		]
	key = []
	periods = []
	labels = []
	options = [{"numCols":4, "chartType":"line", "height":150, "scaleBy":"group"}]
	chartId = [{"type":"smallmultiples"}]
	df.fillna('', inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template,options=options, data=chartData, chartId=chartId, chartName="vic-lga-trend-2021")

makeLgaTrend(long_stack)
