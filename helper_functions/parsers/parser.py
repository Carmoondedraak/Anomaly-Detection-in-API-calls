
class Create_Dataset(object):
    '''object that generates the dataset dataframe saved in pickle format'''

    def __init__(self, data, coockie, ip_address, file):
        '''creates the dataset and saves it to a pickle file
            *******************
            Input:
            * data - the request,response and body.
            * coockie - the coockie that is inherent to the http session - the user coockie

            Output:
            * creates a pickle file in '/data/dataframe.pkl'
            '''

        # parse the requests and create a dict    
        for i, requests in enumerate(data):
            header, req, json_part = self.parse_request(requests[0])
            data_dict = self.create_dict(header,req, json_part)
            data_dict['coockie'] = coockie
            data_dict['ip address'] = ip_address
            data_dict['request time'] = requests[1]
            df1 = pd.DataFrame([data_dict])
            
            # add the different request data together in pandas dataframe 
            if i == 0:
                df = df1
                
            else:
                df = pd.concat([df,df1],ignore_index=True)
        
        # save pandas dataframe to pickle and add to existing pickle when new user is spawned
        if os.path.isfile(file):
            df_prev =  pd.read_pickle(file)
            df = pd.concat([df,df_prev],ignore_index=True)
        df.to_pickle(file)

    def parse_request(self, http_r):
        '''parses the request into header, full http request and response except header and json part, json part'''
        
        # take of the website html, this is not intersting for detection
        if '<!DOCTYPE html>' in http_r:
            http_r = http_r.split('<!DOCTYPE html>')[0]
 
        # split into request, response and json body 
        if '[' in http_r:
            http_r = http_r.split('[')
            json_part = http_r[1]
            req,res = self.parse_req_res(http_r[0])

        else:
            req,res = self.parse_req_res(http_r)
            json_part = http_r[-1].split('{')
        
        # split into seperate lines and sanitize
        req = req.split('<')
        res = res.split('>')
        req = self.sanitize_request(req + res) 

        # split and santize http header
        header  = self.sanitize_request(req[0].split(' '))
        return header,req,json_part

    def parse_req_res(self, http_r):
        '''parse thet into request and response'''

        # the two enters between request and response can be encoded as '\n\n>' or '\r\n\r\n>'.
        # therefore if either one is encountered they should be split accordingly
        if '\n\n>' in http_r:
            request_part = http_r.split('\n\n>')[0]
            response_part =  http_r.split('\n\n>')[1]
        else:
            request_part = http_r.split('\r\n\r\n>')[0]
            response_part =  http_r.split('\r\n\r\n>')[1]
        return request_part, response_part



    def sanitize_request(self, req):
        '''Sanitize the request data'''
        # remove trailing and starting white spaces, commas, enters and < for readability
        req = [x for x in req if x != '' and x != ',' and x != ', ' and x != ' ,' and x!= ' \n'and x !='<']    

        # remove the ; because csv does not like them and puts them in different columns
        req = [x.replace(';','&') for x in req]
        req = [x.replace('\r','') for x in req]
        req = [x.replace('<','') for x in req]
        req = [x.replace('>','') for x in req]
        
        #further sanitizes the headers
        req = [x.replace("\n","") for x in req]
        req = [x.replace('"',"") for x in req]
        req = [x.replace("{","") for x in req]
        # req = [x.replace(' ','') for x in req if x[0]==' ']
        
        return req

    def create_dict(self, header, req, json_part):
        '''creates a dictionary with all the data from the HTTP request and response
            ************************************************************************
            Input: 
            * header - the first line of the http request
            * req - the full request except the header and the json body
            * json_part - the json body
            ************************************************************************
            Output:
            * data_dict - the dictionary of the whole data
            ************************************************************************
        '''
        data_dict = OrderedDict()
        # create header in data dict
        data_dict.update({"type": header[0], "url": header[1], "protocol": header[2] })
        other_lines = []

        # add each line of the request/response as key and value to the dict (most of them are seperated with ':' in the middle)
        for line in req[1:]:
            if ':' in line:
                key, value = line.split(":")[0],':'.join(map(str,line.split(":")[1:]))
                data_dict.update({key : value})
            else:
                # if they are not it is the response code or something that is not important (e.g. coock is set, " ")
                other_lines.append(line)
                if 'HTTP' in line:
                    data_dict['response code'] = line

        data_dict['body'] = json_part
        return data_dict

    def dataframe_to_csv(self, data, file_name):
        '''Push the dataframe to csv file'''
        csv = data.to_csv(file_name, mode='a', index=False)



cr_data = Create_Dataset(data, coockie, ip_address, 'data/anomalies_parsed.pkl')
