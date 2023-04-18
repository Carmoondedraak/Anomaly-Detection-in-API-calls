from dataclasses import dataclass
from http.client import responses
import re
import urllib, json
from datetime import datetime
import json,urllib.request
import csv
from xml.dom.pulldom import START_ELEMENT
import pandas as pd
import sys   
import requests   
from requests_toolbelt.utils import dump
from collections import OrderedDict
stringy = '''
< GET /catalogue?tags=black%2Cblack%2Csport%2Cskin%2Cgreen%2Caction%2Cskin%2Cskin%2Cgeek&page=1&size=100 HTTP/1.1
< Host: 172.18.0.4:30001
< User-Agent: python-requests/2.27.1
< Accept-Encoding: gzip, deflate, br
< Accept: */*
< Connection: keep-alive
< 

> HTTP/1.1 200 OK
> x-powered-by: Express
> set-cookie: md.sid=s%3AEKxwF_I0Fd1tGMz2dI6IVKYlB3M0vQVR.87ULKBXU%2FlnqueWt5Jt1AsM5j1cwV85ew0YRgUU531g; Path=/; HttpOnly
> date: Thu, 09 Feb 2023 21:12:20 GMT
> x-envoy-upstream-service-time: 131
> server: istio-envoy
> x-envoy-decorator-operation: front-end.sock-shop.svc.cluster.local:80/*
> transfer-encoding: chunked
> 
[{"id":"03fef6ac-1896-4ce8-bd69-b798f85c6e0b","name":"Holy","description":"Socks fit for a Messiah. You too can experience walking in water with these special edition beauties. Each hole is lovingly proggled to leave smooth edges. The only sock approved by a higher power.","imageUrl":["/catalogue/images/holy_1.jpeg","/catalogue/images/holy_2.jpeg"],"price":99.99,"count":1,"tag":["action"]},{"id":"510a0d7e-8e83-4193-b483-e27e09ddc34d","name":"SuperSport XL","description":"Ready for action. Engineers: be ready to smash that next bug! Be ready, with these super-action-sport-masterpieces. This particular engineer was chased away from the office with a stick.","imageUrl":["/catalogue/images/puma_1.jpeg","/catalogue/images/puma_2.jpeg"],"price":15,"count":820,"tag":["black","sport"]},{"id":"808a2de1-1aaa-4c25-a9b9-6612e8f29a38","name":"Crossed","description":"A mature sock, crossed, with an air of nonchalance.","imageUrl":["/catalogue/images/cross_1.jpeg","/catalogue/images/cross_2.jpeg"],"price":17.32,"count":738,"tag":["action"]},{"id":"819e1fbf-8b7e-4f6d-811f-693534916a8b","name":"Figueroa","description":"enim officia aliqua excepteur esse deserunt quis aliquip nostrud anim","imageUrl":["/catalogue/images/WAT.jpg","/catalogue/images/WAT2.jpg"],"price":14,"count":808,"tag":["green"]},{"id":"837ab141-399e-4c1f-9abc-bace40296bac","name":"Cat socks","description":"consequat amet cupidatat minim laborum tempor elit ex consequat in","imageUrl":["/catalogue/images/catsocks.jpg","/catalogue/images/catsocks2.jpg"],"price":15,"count":175,"tag":["green"]},{"id":"a0a4f044-b040-410d-8ead-4de0446aec7e","name":"Nerd leg","description":"For all those leg lovers out there. A perfect example of a swivel chair trained calf. Meticulously trained on a diet of sitting and Pina Coladas. Phwarr...","imageUrl":["/catalogue/images/bit_of_leg_1.jpeg","/catalogue/images/bit_of_leg_2.jpeg"],"price":7.99,"count":115,"tag":["skin"]},{"id":"d3588630-ad8e-49df-bbd7-3167f7efb246","name":"YouTube.sock","description":"We were not paid to sell this sock. It's just a bit geeky.","imageUrl":["/catalogue/images/youtube_1.jpeg","/catalogue/images/youtube_2.jpeg"],"price":10.99,"count":801,"tag":["geek"]},{"id":"zzz4f044-b040-410d-8ead-4de0446aec7e","name":"Classic","description":"Keep it simple.","imageUrl":["/catalogue/images/classic.jpg","/catalogue/images/classic2.jpg"],"price":12,"count":127,"tag":["green"]}]
'''
def parse_request(http_r):
    http_r = http_r.split('[')
    request_part = http_r[0].split('\n\n>')[0].split('\n<')
    response_part =  http_r[0].split('\n\n>')[1].split('\n>')
    json_part = http_r[1]
    
    req = sanitize_request(request_part + response_part) 
    header  = sanitize_request(req[0].split(' '))
    return header, req,json_part


def sanitize_request(req):
    '''Sanitize the request data'''
    # remove trailing and starting white spaces, commas and enters for readability
    req = [x for x in req if x != '' and x != ',' and x != ', ' and x != ' ,' and x!= ' \n']    

    # remove the ; because csv does not like them and puts them in different columns
    req = [x.replace(';','&') for x in req]
    return req

def create_dict(header, req, json_part):
    data_dict = OrderedDict()
    data_dict.update({"type": header[0], "url": header[1], "protocol": header[2] })
    other_lines = []
    for line in req[1:]:
        if ':' in line:
            key, value = line.split(":")[0],line.split(":")[1]
            data_dict.update({key : value})
        else:
            other_lines.append(line)
            if line != '':
                data_dict['response code'] = line

    data_dict['body'] = json_part
    return data_dict


def get_data(csv_file):
    header, req, json_part = parse_request(stringy)
    data_dict = create_dict(header,req, json_part)
    df = pd.DataFrame.from_dict([data_dict])
    csv = df.to_csv(csv_file, index=False)

get_data('hello.csv')
# variables
# start_time = "2023-01-18T12%3A13%3A33"
# end_time = "2023-01-18T12%3A13%3A33.461Z"

# def get(url):
#     params = {
#     'tags': 'magic',
#     'page': 1,
#     'size': 100
#     }
#     requests.Session()
#     res = requests.get(url + '/catalogue', params=params)
#     return dump.dump_all(res).decode('utf-8')
# get('http://172.18.0.4:3001')
# #functions
# def get_json(end_time):
#     '''Gets the json file of the incoming api calls to the sockshop application'''

#     # url to apiclarity api call endpoint of the table
#     url = "http://127.0.0.1:9999/api/apiEvents?startTime="+ start_time+ "&endTime="+ end_time+"&showNonApi=false&page=1&pageSize=50&sortKey=time&sortDir=DESC"
#     data = urllib.request.urlopen(url).read()
#     output = json.loads(data)
#     return output

# def get_time():
#     '''Get the time for right now (in greenwich time)'''
#     now = datetime.now()
#     current_time = now.strftime("%Y-%m-%dT%H:%M:%S")
#     current_time = current_time.replace(':','%3A')
#     return current_time

# def get_dataframe(json_file):
#     '''Turn the json file into a csv file
#         *  json_file - is the json file that needs to be turned into a csv file
#         * csv_file - is the filename that the csv file needs to be stored as
#     '''
#     assert json_file['total'] > 0, f"expected to see some API call data instead received empty data"
#     data = json_file['items']
#     header = list(data[0].keys())
#     df = pd.DataFrame(data)
#     return df

# def get_csv(df, csv_file):
#     '''Turn the datafram into a csv file
#         * dataframe - is the pandas dataframe
#         * csv_file - is the filename that the csv file needs to be stored as
#     '''
#     csv = df.to_csv(csv_file, index=False)
#     return csv

# def clean_data(df):
#     '''remove duplicate rows and replace NaNs with zeroes'''


# # script
# if __name__ == "__main__":
#     time = get_time()
    
#     for i in range(2):
#         json_file = get_json(time)
#         time = json_file['items'][-1]['time'].replace(':','%3A')
#         df1 = get_dataframe(json_file)
        
#         if i == 0:
#             df = df1
#         else:
#             df = pd.concat([df,df1],ignore_index=True)

#     if len(sys.argv) < 2:
#         raise RuntimeError("add a filename to the input ~ behine the command")
#     csv_file = get_csv(df, sys.argv[1])

                                                                                                                                        


