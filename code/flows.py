import plotly.graph_objects as go
from collections import OrderedDict
import seaborn as sns
import random
import numpy as np
from collections import defaultdict

class APIflows2:
    def __init__(self,data):
        self.data = data
        self.flowdict = OrderedDict()
        self.paths = []
        self.flow()
        self.path_info()
    
    def flow(self):
        last = 0
        cate = cat_enc(self.data['request_uri'])
        frames = {}
        for i in range(len(self.data)):
            if math.isnan(float(self.data['prev_request_in'][i])):
                self.add_flow_to_dict(0,cate[i])

                frames[self.data['frame'][i]] = [((0,cate[i]))]
            else:
                idx = self.data[self.data['frame']==self.data['prev_request_in'][i]].index.values

                if len(idx) > 1:
                    idx = [idx.flat[np.abs(idx - last).argmin()]]
                elif len(idx) < 1 or idx > i:
                    frames[self.data['frame'][i]] = [((0,cate[i]))]
                    continue
                
                last= idx[0]
                idx = idx[0]
                self.add_flow_to_dict(cate[idx], cate[i])
                frames[self.data['frame'][idx]].append(((cate[idx],cate[i])))
                frames[self.data['frame'][i]] = frames[self.data['frame'][idx]] 
                del frames[self.data['frame'][idx]]
        self.paths = list(frames.values())


                    
                    
    def add_flow_to_dict(self,flow1,flow2):
        '''Checks whether the flow is from the same user (by comparing coockies) and adds 
            them to the flow dict and source and target lists
            
            ***input***
            flow1 & flow2: the flows of the first and second user            
            '''
        if ((flow1,flow2)) not in self.flowdict:
            self.flowdict[((flow1,flow2))] = 1

        else:
            self.flowdict[((flow1,flow2))] += 1
            
    def path_info(self):    
        '''Get the shortest and longest paths
            Also get which paths are taken most often'''
        self.shortest = self.paths
        self.shortest.sort(key=lambda l: (len(l), l))
        self.numbers = {}
        
        for i in range(len(self.paths)):
            if tuple(self.paths[i]) in list(self.numbers.keys()):
                self.numbers[tuple(self.paths[i])] += 1  
            
            else:    
                self.numbers[tuple(self.paths[i])] = 1

def cat_enc(col):
    '''encode one column into categorical encoding'''
    
    col = pd.factorize(col)[0] + 1
    return col

if __name__="__main__"
    flows_a = APIflows2(data_a)
    flows_n =  APIflows2(data_n)