import scraperwiki
import pandas as pd
from yachtCharter import yachtCharter
from datetime import timedelta
import requests
from vic import getData

#%%

getData()

#%%
pd.options.mode.chained_assignment = None  # default='warn'
data = scraperwiki.sqlite.select("* from data")
latest = requests.get('https://interactive.guim.co.uk/docsdata/1XeCK-B3eOKKfN-BCXbV0Ln46_xT7jE6ozTAJ7pAPRvo.json').json()['sheets']

#%%

test = ""
# test = "-test"

cols = ["Local, known origin", "Local, unknown origin", "Local, unknown origin"]

df = pd.DataFrame(data)

df = df.rename(columns={"Acquired in Australia, unknown source": "Local, unknown origin", "Contact with a confirmed case": "Local, known origin","Travel overseas":"Overseas" })

df.date = pd.to_datetime(df.date, format="%Y-%m-%d")

df = df.set_index('date')

last_5 = df[-5:]
last_5 = last_5.dropna(how='all')

df2 = pd.concat([df[:-5], last_5])

#%%
newData = latest['VIC']

new_df = pd.DataFrame(newData)
new_df.date = pd.to_datetime(new_df.date, format="%d-%m-%Y")
new_df = new_df.set_index('date')
new_df = new_df.apply(pd.to_numeric)
new_total = new_df
new_df = new_df.drop(['Total'], axis=1)

df3 = df2.append(new_df)
df3 = df3[~df3.index.duplicated()]

#%%	

short = df3["2020-05-01":]

# short_new = pd.concat([short, new_df])

just_local = pd.DataFrame()
just_local['Local and under investigation'] = df3[["Local, unknown origin", "Local, known origin", "Under investigation"]].sum(axis=1)
just_local['Overseas'] = df3['Overseas'] 
just_local['Local and under investigation, 7 day average'] = just_local['Local and under investigation'].rolling(7).mean()
just_local['Overseas, 7 day average'] = just_local['Overseas'].rolling(7).mean()
just_local['cumulative'] = just_local['Local and under investigation'].cumsum()
just_local['pct_change'] = just_local['cumulative'].pct_change()
just_local = just_local["2020-01-25":]
lastUpdated = df3.index[-1]
lastUpdatedStr = lastUpdated.strftime('%Y-%m-%d')
just_local.index = just_local.index.strftime('%Y-%m-%d')

short.index = short.index.strftime('%Y-%m-%d')

#%%

def makeLocalLine(df):

 	# lastUpdatedInt =  df.index[-1]
	
 	template = [
 			{
				"title": "Trend in local and overseas-related transmission of Covid-19 in Victoria",
				"subtitle": "Showing the 7 day rolling average of locally and overseas-acquired cases, with those under investigation added to the local category. Last updated {date}".format(date=lastUpdatedStr),
				"footnote": "",
				"source": " | Health and Human Services Victoria",
				"dateFormat": "%Y-%m-%d",
				"yScaleType":"",
				"xAxisLabel": "",
				"yAxisLabel": "",
				"minY": "",
				"maxY": "",
				"x_axis_cross_y":"0",
				"periodDateFormat":"",
				"margin-left": "50",
				"margin-top": "30",
				"margin-bottom": "20",
				"margin-right": "10"
 			}
		]
 	key = []
 	periods = []
 	labels = []
 	chartId = [{"type":"linechart"}]
 	df.fillna(0, inplace=True)
 	df = df.reset_index()
 	chartData = df.to_dict('records')

 	yachtCharter(template=template, data=chartData, chartId=[{"type":"linechart"}], chartName="local-trend-vic-corona-2020{test}".format(test=test))

makeLocalLine(just_local[['Local and under investigation, 7 day average','Overseas, 7 day average']])

#%%

def makeSourceBars(df):

	# lastUpdatedInt =  df.index[-1]
	
	template = [
			{
				"title": "Source of Covid-19 infections in Victoria since 1 May",
				"subtitle": "Showing the daily count of new cases by the source of infection. The most recent day is from a media release or press conference, and should be considered preliminary. Last updated {date}".format(date=lastUpdatedStr),
				"footnote": "",
				"source": " | Health and Human Services Victoria",
				"dateFormat": "%Y-%m-%d",
				"xAxisLabel": "",
				"yAxisLabel": "Cases",
				"timeInterval":"day",
				"tooltip":"TRUE",
				"periodDateFormat":"",
				"margin-left": "50",
				"margin-top": "20",
				"margin-bottom": "20",
				"margin-right": "20",
				"xAxisDateFormat": "%b %d"
				
			}
		]
	key = [
		{"key":"Local, unknown origin","colour":"#d73027"},
		{"key":"Local, known origin","colour":"#f46d43"},
		{"key":"Overseas","colour":"#74add1"},
		{"key":"Under investigation", "colour":"#8073ac"}
			]
	periods = []
	labels = [{"x1":"2020-05-12", "y1":7, "y2":24, "text":"Restrictions eased", "align":"start"}, 
			   {"x1":"2020-06-1", "y1":9, "y2":18, "text":"Restrictions eased", "align":"middle"},
			   {"x1":"2020-06-22", "y1":19, "y2":26, "text":"Restrictions tightened", "align":"end"}
			   ]
	chartId = [{"type":"stackedbar"}]
	df.fillna('', inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template, data=chartData, chartId=chartId, chartName="infection-source-vic-health-corona-2020-unknowns-bar{test}".format(test=test), labels=labels, key=key)

makeSourceBars(short[["Local, unknown origin", "Local, known origin", "Overseas", "Under investigation"]])


def makeSourceBarsLong(df):

	# lastUpdatedInt =  df.index[-1]
	
	template = [
			{
				"title": "Source of Covid-19 infections in Victoria",
				"subtitle": "Showing the daily count of new cases by the source of infection. The most recent day is from a media release or press conference, and should be considered preliminary. Last updated {date}".format(date=lastUpdatedStr),
				"footnote": "",
				"source": " | Health and Human Services Victoria",
				"dateFormat": "%Y-%m-%d",
				"xAxisLabel": "",
				"yAxisLabel": "Cases",
				"timeInterval":"day",
				"tooltip":"TRUE",
				"periodDateFormat":"",
				"margin-left": "50",
				"margin-top": "20",
				"margin-bottom": "20",
				"margin-right": "20",
				"xAxisDateFormat": "%b %d"
				
			}
		]
	key = [
		{"key":"local","colour":"#d73027"},
		{"key":"overseas","colour":"#74add1"}
			]
	periods = []

	chartId = [{"type":"stackedbar"}]
	df.fillna('', inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template, data=chartData, chartId=chartId, chartName="infection-source-vic-health-corona-2020-long-bar{test}".format(test=test), key=key)

makeSourceBarsLong(just_local[['Local and under investigation','Overseas']])


#%%
# df2 = df2.apply(pd.to_numeric)

df2['New cases'] = df2.sum(axis=1)
vic_total = df2.append(new_total)
vic_total = vic_total[~vic_total.index.duplicated()]
vic_total.index = vic_total.index.strftime('%Y-%m-%d')

def makeTotalBars(df):

	# lastUpdatedInt =  df.index[-1]
	
	template = [
			{
				"title": "Daily Covid-19 infections in Victoria",
				"subtitle": "Showing the daily count of new cases. The most recent day is from a media release or press conference, and should be considered preliminary. Last updated {date}".format(date=lastUpdatedStr),
				"footnote": "",
				"source": " | Health and Human Services Victoria",
				"dateFormat": "%Y-%m-%d",
				"xAxisLabel": "",
				"yAxisLabel": "Cases",
				"timeInterval":"day",
				"tooltip":"TRUE",
				"periodDateFormat":"",
				"margin-left": "50",
				"margin-top": "20",
				"margin-bottom": "20",
				"margin-right": "20",
				"xAxisDateFormat": "%b %d"
				
			}
		]

	periods = []
	key = [{"key":"New cases","colour":"rgb(204, 10, 17)"}]
	chartId = [{"type":"annotatedbarchart"}]
	df.fillna('', inplace=True)
	df = df.reset_index()
	chartData = df.to_dict('records')

	yachtCharter(template=template, data=chartData, chartId=chartId, chartName="vic-total-corona-cases{test}".format(test=test), key=key)

makeTotalBars(vic_total[['New cases']])

#%%


