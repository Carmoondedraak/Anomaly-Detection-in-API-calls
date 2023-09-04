import plotly.graph_objects as go
from collections import OrderedDict
import seaborn as sns
import random
import numpy as np
from collections import defaultdict
import pandas as pd
import math

class APIflows2:
    def __init__(self,data):
        self.data = data
        self.flowdict = OrderedDict()
        self.paths = []
        self.idxperflow = {}
        self.flow()
        self.path_info()
    
    def flow(self):
        last = 0
        cate = cat_enc(self.data['request_uri'])
        frames = {}
        for i in range(len(self.data)):
            if math.isnan(float(self.data['prev_request_in'][i])):
                self.add_flow_to_dict(0,cate[i])
                self.idxperflow[i] = (0,cate[i])

                frames[self.data['frame'][i]] = [((0,cate[i]))]
            else:
                # finding the frames that correspond with the prev request
                idx = self.data[self.data['frame']==self.data['prev_request_in'][i]].index.values

                if len(idx) > 1:
                    # idx is a list of frames, since sometimes the framenumbers are reused in the dataset. The numbered frames do not go to infinity, so we need to get the one that 
                    # contains the right frame of the list of frames with the same number
                    # we do this by taking the index that is the closest to the current frame
                    idx = [idx.flat[np.abs(idx - last).argmin()]]
  
                elif len(idx) < 1 or idx > i:
                    # sometimes there is no corresponding frame, or the frame is outside of the scope of the pcap dataset. Then we want nothing to be added to the dict
                    frames[self.data['frame'][i]] = [((0,cate[i]))]
                    continue
                
                last = idx[0]
                idx = idx[0]
                self.add_flow_to_dict(cate[idx], cate[i])
                self.idxperflow[i] = (cate[idx],cate[i])
                # print('idx',idx)
                # print(frames[self.data['frame'][idx]], idx)
                # some times the index of the frame is not present in the frames than we want to skip this
                if self.data['frame'][idx] not in frames:
                    print('hello')
                    pass
                else:
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

if __name__=="__main__":
    flows_a = APIflows2(data_a)
    flows_n =  APIflows2(data_n)