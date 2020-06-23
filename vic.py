import requests
import json
import scraperwiki
from datetime import datetime, date, timedelta

url = 'https://wabi-australia-southeast-api.analysis.windows.net/public/reports/querydata?synchronous=true'

headers = {
	"Accept": "application/json, text/plain, */*",
	"ActivityId": "a1955107-c5d9-12b5-87a4-561001265ed6",
	"Content-Type": "application/json;charset=UTF-8",
	"Origin": "https://app.powerbi.com",
	"Referer": "https://app.powerbi.com/view?r=eyJrIjoiODBmMmE3NWQtZWNlNC00OWRkLTk1NjYtMjM2YTY1MjI2NzdjIiwidCI6ImMwZTA2MDFmLTBmYWMtNDQ5Yy05Yzg4LWExMDRjNGViOWYyOCJ9",
	"RequestId": "c1ef00f5-e7b9-fe25-927d-a8f673615040",
	"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
	"X-PowerBI-ResourceKey": "80f2a75d-ece4-49dd-9566-236a6522677c",
	"modelID":"1959902"
}

payload = {"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"l","Entity":"Linelist","Type":0},{"Name":"d","Entity":"dimDate","Type":0}],"Select":[{"Column":{"Expression":{"SourceRef":{"Source":"l"}},"Property":"acquired_n"},"Name":"Linelist.acquired_n"},{"Measure":{"Expression":{"SourceRef":{"Source":"l"}},"Property":"Cases"},"Name":"Linelist.Cases"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"Date"}}],"Values":[[{"Literal":{"Value":"datetime'2020-05-07T00:00:00'"}}]]}}}],"OrderBy":[{"Direction":2,"Expression":{"Measure":{"Expression":{"SourceRef":{"Source":"l"}},"Property":"Cases"}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0,1]}]},"DataReduction":{"DataVolume":3,"Primary":{"Top":{}}},"Version":1}}}]},"QueryId":"","ApplicationContext":{"DatasetId":"5b547437-24c9-4b22-92de-900b3b3f4785","Sources":[{"ReportId":"964ef513-8ff4-407c-8068-ade1e7f64ca5"}]}}],"cancelQueries":[],"modelId":1959902}

date = datetime.strftime(datetime.now(), "%Y-%m-%d")

print(date)


clean = []

sdate = datetime(2020, 5, 1)
edate = datetime.now()

delta = edate - sdate


for i in range(delta.days + 1):
	print(i)
	day = sdate + timedelta(days=i)
	newDate = datetime.strftime(day, "%Y-%m-%dT%H:%M:%S")
	print(newDate) 
	newLoad = {"version":"1.0.0","queries":[{"Query":{"Commands":[{"SemanticQueryDataShapeCommand":{"Query":{"Version":2,"From":[{"Name":"l","Entity":"Linelist","Type":0},{"Name":"d","Entity":"dimDate","Type":0}],"Select":[{"Column":{"Expression":{"SourceRef":{"Source":"l"}},"Property":"acquired_n"},"Name":"Linelist.acquired_n"},{"Measure":{"Expression":{"SourceRef":{"Source":"l"}},"Property":"Cases"},"Name":"Linelist.Cases"}],"Where":[{"Condition":{"In":{"Expressions":[{"Column":{"Expression":{"SourceRef":{"Source":"d"}},"Property":"Date"}}],"Values":[[{"Literal":{"Value":"datetime'{newDate}'".format(newDate=newDate)}}]]}}}],"OrderBy":[{"Direction":2,"Expression":{"Measure":{"Expression":{"SourceRef":{"Source":"l"}},"Property":"Cases"}}}]},"Binding":{"Primary":{"Groupings":[{"Projections":[0,1]}]},"DataReduction":{"DataVolume":3,"Primary":{"Top":{}}},"Version":1}}}]},"QueryId":"","ApplicationContext":{"DatasetId":"5b547437-24c9-4b22-92de-900b3b3f4785","Sources":[{"ReportId":"964ef513-8ff4-407c-8068-ade1e7f64ca5"}]}}],"cancelQueries":[],"modelId":1959902}
	# print(newLoad)

	r = requests.post(url, data=json.dumps(newLoad), headers=headers)
	data = json.loads(r.text)

	results = data['results'][0]['result']['data']['dsr']['DS'][0]['PH'][0]['DM0']
	print(json.dumps(results, indent=4))
	newRow = {}
	newRow['date'] = datetime.strftime(day, "%Y-%m-%d")
	for d in results:
		if len(d['C']) == 2:
			newRow[d['C'][0]] = d['C'][1]
		if len(d['C']) == 1:
			newRow[d['C'][0]] = d['R']
	print(newRow)	

	scraperwiki.sqlite.save(unique_keys=["date"], data=newRow, table_name="data")
