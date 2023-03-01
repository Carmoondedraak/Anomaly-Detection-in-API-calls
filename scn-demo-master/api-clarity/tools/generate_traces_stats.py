import math
import random
import requests
import json
import uuid
import datetime
import sys
import os


class ApiClarityClient(object):
	def __init__(self, apiurl, internalurl):
		self._apiurl = apiurl
		self._internalurl = internalurl
		self._session = None
	 
	def _api_url(self, url):
		return self._apiurl + url
	
	def _internal_url(self, url):
		return self._internalurl + url
	
	def upload_provided_spec(self, specfile, apiId):
		with open(specfile) as f:
			spec = json.load(f)
		
		payload = json.dumps({
			"rawSpec": json.dumps(spec)
		})
		print(payload)
		headers = {
			'Content-Type': 'application/json; charset=utf-8'
		}
		r = requests.put(self._api_url(f"/apiInventory/{apiId}/specs/providedSpec"), headers=headers,  data=payload)
		
		if r.status_code >= 200 and r.status_code < 300:
			b = r.json()
		else:
			b = r.text
		
		print(f"uploaded:{r} {b}")
  
	def get_inventory_item(self, apiId):
		rep = requests.get(self._api_url(f"/apiInventory/{apiId}"))
		if rep.status_code >= 200 < 300: b = rep.json()
		else: b = rep.text
		
		print(f"inventory:{rep} {b}")
		
	def post_trace(self, source, destination, method, path, reqtime, reptime):
		payload = json.dumps({
			"requestID": f"{uuid.uuid4()}",
			"scheme": "http",
			"destinationAddress": destination,
			"destinationNamespace": "XXXDESTNAMESPACEXXX",
			"sourceAddress": source,
			"request": {
				"method": method,
				"path": path,
				"host": "www.httpbin.org:8000",
				"common": {
					"time": int(reqtime.timestamp() * 1000),
					"version": "1",
					"headers": [],
					"body": "",
					"TruncatedBody": False
				}
			},
			"response": {
				"statusCode": "200",
				"common": {
					"time": int(reptime.timestamp() * 1000),
					"version": "1",
					"headers": None,
					"body": "",
					"TruncatedBody": False
				}
			}
		})
		headers = {
			'Content-Type': 'application/json'
		}
		r = requests.post(self._internal_url("/telemetry"), headers=headers, data=payload)
		
		if r.status_code >= 200 and r.status_code < 300:
			b = r.json()
		else:
			b = r.text
		
		print(f"{reqtime} {reptime} trace:{r} {b}")

def reqpersec(sec):
	freq = 0.5
	offset = 20
	amplitude = 10
	
	reqpersec = int(round(amplitude * math.sin(freq*sec) + offset))
	reqpersec += random.randint(int(-0.05*reqpersec), int(0.05*reqpersec))
	if reqpersec <= 0: reqpersec = 0
	return reqpersec

def generate_trace(apiclarity_base, apiId, specFile):
	now = datetime.datetime.now()
	minutes = 2
	print(f"{apiclarity_base}")
	client = ApiClarityClient(f"{apiclarity_base}:8080/api", f"{apiclarity_base}:9000/api")
	source = "10.1.1.1:3333"
	destination = "101.22.2.32:8080"
	method = "GET"
	path = "/api/dashboard/apiUsage/mostUsed"
	
	reqtime = now - datetime.timedelta(hours=1, minutes=minutes, seconds=1)
	reptime = reqtime + datetime.timedelta(milliseconds=233)
	
	client.post_trace(source, destination, method, path, reqtime=reqtime, reptime=reptime)
	client.upload_provided_spec(specFile, apiId)
	
	reqtime = now - datetime.timedelta(hours=1, minutes=minutes)
	
	for sec in range(minutes*60):
		nreq = reqpersec(sec)
		if nreq == 0:
			reqtime += datetime.timedelta(seconds=1)
			continue
		delta = int(round(1000 / nreq))
		for r in range(nreq):
			art = getrtime(sec)
			if sec > minutes*60 - 3:
				art = art*5
			reptime = reqtime + datetime.timedelta(milliseconds=random.randint(art-50, art+50))
			client.post_trace(source, destination, method, path, reqtime=reqtime, reptime=reptime)
			reqtime += datetime.timedelta(milliseconds=delta)
	
def getrtime(sec):
	return 3*sec+100
	
# def go2():
# 	ndays = 10
# 	todaytd = datetime.datetime.fromisoformat(datetime.date.today().isoformat())
# 	client = ApiClarityClient("http://localhost:8080/api", "http://localhost:9000/api")
# 	source = "10.1.1.1:3333"
# 	destination = "10.2.2.2:8080"
# 	method = "GET"
# 	path = "/api/dashboard/apiUsage/mostUsed"
#
# 	reqtime = reqtime = todaytd - datetime.timedelta(days=ndays, hours=1)
# 	reptime = reqtime + datetime.timedelta(milliseconds=233)
#
# 	client.post_trace(source, destination, method, path, reqtime=reptime, reptime=reptime)
#
# 	client.upload_provided_spec("provided_spec.json", 8)
#
# 	reqtime = todaytd - datetime.timedelta(days=10)
# 	for i in range(ndays):
# 		for sec in range(60 * 60 * 24):
# 			nreq = reqpersec(sec)
# 			if nreq == 0:
# 				reqtime += datetime.timedelta(seconds=1)
# 				continue
# 			delta = int(round(1000 / nreq))
# 			for r in range(nreq):
# 				if sec > range(60 * 60 * 24) - 3:
# 				getrtime(sec)
# 				reptime = reqtime + datetime.timedelta(milliseconds=random.randint(10, 200))
# 				client.post_trace(source, destination, method, path, reqtime=reqtime, reptime=reptime)
# 				reqtime += datetime.timedelta(milliseconds=delta)


if __name__ == "__main__":
	if len(sys.argv) < 3 :
		print("ERROR: not enough arguments")
		sys.exit(1)
	
	apiId = sys.argv[1]
	specFile = sys.argv[2]
	apiclarity_base = os.getenv("APICLARITY_BASE", "http://localhost")
	generate_trace(apiclarity_base, apiId, specFile)
