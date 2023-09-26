import copy
import math
import argparse
import pandas as pd
from flows import *
from sklearn.utils import shuffle
import seaborn as sns
import matplotlib.pyplot as plt


class Data_Preprocess():
    '''
        data_n: the dataset with the normal data (pandas)
        data_a: the dataset with the abnormal data (pandas)
        even: the create even dataset of normal and abnormal data (True or False)
        health: to remove the health calls that are present in the environment (True or False)
        data_remove: remove specific data (set of names)
        cosine: if you want to remove features based on consine similarity (True or False)
        to_keep: set of values to keep (set of names)
        continuous: list of continuous data
        numerical: list of numerical data
    '''
    def __init__(self, data_n, data_a):
        self.data_n = copy.deepcopy(data_n)
        self.data_a = copy.deepcopy(data_a)
        self.data = [self.data_n,self.data_a]
  
    def create_dataset(self, to_keep=set(), data_remove=set(), health=True, even=True, cosine = False,continuous=[],numerical=[]):
        self.to_keep = to_keep
        self.data_remove = data_remove
        self.continuous = continuous
        self.numerical = numerical 
        data = self.data
        self.specific_preprocessing(data)
        if len(self.data_remove) > 0:
            data = self.remove_unessecary_data(data)
            
        if len(self.to_keep) > 0:
            data = self.remove_specific_data(data)

        if health == True:
            data = self.remove_health_calls(data)
            
        if even == True:
            data = self.even_dataset(data)
        if len(self.continuous) > 0 and len(self.numeric) > 0:

            for i in range(2):
                data[i] = self.change_values(data[i])
        return data

    def remove_unessecary_data(self, data):
        '''remove data that has no changing values or needs to be removed'''
        for i in range(len(data)):
            data[i] = data[i].fillna(0)
            print('hallo')
            for col in data[i].columns:
                if col in data_remove or len(data[i][col].value_counts()) == 1:
                    print('dataset', i, 'removed', col,'with only',len(data[i][col].value_counts()), 'specific values')
                    data[i].pop(col)
        print('done removing unnessecary data')
        return data


    def even_dataset(self, data):
        '''create even datasets and remove columns that are not present in either one'''
        if len(data[0]) > len(data[1]):
            data[0] = data[0].sample(n=len(data[1]))

        else:
            data[1] = data[1].sample(n=len(data[0]))
        return data

    def cosine_similarity(self, df):
        '''calculate cosine similarity of all the features'''
        feats = df.columns
        cos_sim_a = {}
        for feat in range(len(feats)):
            for feat2 in range(len(feats)):
                if feat != feat2:
                    cos_sim = (df[feats[feat]] @ df[feats[feat2]].T) / (np.linalg.norm(df[feats[feat]])* np.linalg.norm(df[feats[feat2]]))
                    if (feats[feat2],feats[feat]) not in cos_sim_a.keys():
                        cos_sim_a[feats[feat],feats[feat2]] = cos_sim 
        return cos_sim_a


    def remove_cosine_sim_high(self, cossim, data):
        '''remove features that have a high cosine similarity '''
        highest = {}
        removed = set()
        for key,value in cossim.items():
            if value >= 0.98:
                if key[0] not in highest:
                    highest[key[0]] = 1
                else:
                    highest[key[0]] += 1
                if key[1] not in highest:
                    highest[key[1]] = 1
                else:
                    highest[key[1]] += 1

        for key,value in cossim.items():
            if value >= 0.98 and key[1] not in removed and key[0] not in removed:
                if highest[key[0]] >= highest[key[1]]:
                    data.pop(key[1])
                    removed.add(key[1])
                else:
                    data.pop(key[0])
                    removed.add(key[0])


    def specific_preprocessing(self, data):
        '''remove features specifically (only for this dataset useful)'''
        for j in range(2):
            
            data_p_n = copy.deepcopy(data[j])
            data_p_n.cookie.fillna(data_p_n.set_cookie, inplace=True)

            for i in range(len(data[j]['response_line'])):
                print(data_p_n['response_line'][i])
                if pd.isna(data_p_n['response_line'][i]):
                    data_p_n['response_line'][i] = 0
                elif data_p_n['response_line'][i][0] != 'x':
                    data_p_n['response_line'][i] = 0
                    
            data[j]['response_line'] = data_p_n['response_line']
        return data


    def remove_specific_data(self,data):
        ''' removes all column but a specific set that it is to keep '''

        for i in range(2):
            for col in data[i].columns:
                if col not in self.to_keep:
                    data[i].pop(col)
        data =  [data[0], data[1]]
        return data

    
    
    def remove_health_calls(self,data ):
        '''removes the health calls that are made within  the kubernetes environment'''

        data_n1 = copy.deepcopy(data[0])
        data_a1 = copy.deepcopy(data[1])
        data_n2 = data_n1.where(data_n1['user_agent'] != 'kube-probe/1.25')
        data_a2 =  data_a1.where(data_a1['user_agent'] != 'kube-probe/1.25')
        data_n2 = data_n2.dropna()
        data_a2 = data_a2.dropna()
        data[1] = data_a2
        data[0] = data_n2
        return data

    def change_values(self, data, continuous, categorical):
        '''changes the values from type pyshark field to float or str'''
        
        for col in data.columns:
            if col in continuous: 
                data[col] = data[col].map(float)
                
            elif col in categorical:
                data[col] = data[col].map(str)
        return data

    def Adding_flow_feature(self, data, flow):
        '''This function adds the flow frequency of each call to the dataset
            flow: the object containing the flow information'''

        for j in range(2):
            flows = [] 
            for i in range(len(data[j])):
                if i in flow[j].idxperflow.keys():
                    flows.append(flow[j].flowdict[flow[j].idxperflow[i]])
                else:
                    # if there is no flow for the index in the dataset
                    flows.append(math.nan)
            data[j]['flow_freq'] = flows
            data[j] = data[j].dropna(subset=['flow_freq'],axis=0).reset_index(drop=True)
        self.data = data
        return data

    def save_dataset(self, savefile, data, flag=False):
        '''saves the dataframe to a list of two file <savefile>'''
        if flag == True:
            data.to_pickle(savefile)
        else:
            for i in range(2):
                data[i].to_pickle(savefile[i])  


    def print_dataset(self):
        '''displays the dataframe'''
        display(self.data)

class Train_Val_Test_split():
    '''splits the data into train, validation and test'''

    def __init__(self,percentages = '0.70:0.20:0.10', only_normal = False):
        '''split the data into 70-20-10'''
        self.percentage = percentages
        self.only_normal = only_normal

    def split_dataset(self, data): 
        print('lenght of total data', len(data[0]), len(data[1]))
        self.train_set, self.train_targets = self.train(data[0], data[1])
        self.val_set, self.val_targets = self.val(data[0],data[1])
        self.test_set, self.test_targets = self.test(data[0],data[1])
        print('Length of train data:', len(self.train_set), sum(self.train_targets),' \n length of validation data', len(self.val_set), sum(self.val_targets), '\n length of the test data', len(self.test_set),sum(self.test_targets))

    def train(self, data_n, data_a):
        perc = float(self.percentage.split(':')[0])
        self.train_n = data_n.sample(frac=perc)
        self.train_n['target'] = [0 * i for i in range(len(self.train_n))]
        self.train_a = data_a.sample(frac=perc)
        self.train_a['target'] = [i**0 for i in range(len(self.train_a))]
        print('this here',len(self.train_a), len(self.train_n))

        if self.only_normal == True:
            train = self.train_n

        else:    
            train = pd.concat([self.train_n,self.train_a], ignore_index=True)
        
        train = train.fillna(0)
        train = shuffle(train).reset_index(drop=True)
        targets = train['target']
        self.train_set_t = train
        train = train.drop(['target'],axis=1)
        return train, targets

    def val(self, data_n, data_a):
        perc = float(self.percentage.split(':')[1])
       
        self.val_n = data_n.drop(self.train_n.index)
        perc = ((len(data_n) * perc) /len(self.val_n))
        print(perc, len(self.val_n))
        self.val_n = self.val_n.sample(frac=perc)
        
        self.val_n['target'] = [0 * i for i in range(len(self.val_n))]
        self.val_a = data_a.drop(self.train_a.index)

        self.val_a = self.val_a.sample(frac=perc)  
        self.val_a['target'] = [i**0 for i in range(len(self.val_a))]

        if self.only_normal == True:
            validation = self.val_n

        else:    
            validation = pd.concat([self.val_n,self.val_a], ignore_index=True)
        validation = validation.fillna(0)
        validation = shuffle(validation).reset_index(drop=True)
        targets = validation['target']
        self.val_set_t = validation
        validation = validation.drop(['target'],axis=1)
        return validation,targets 

    def test(self, data_n, data_a):
        self.test_n = data_n.drop(self.train_n.index)
        self.test_n = self.test_n.drop(self.val_n.index)
        self.test_n['target'] = [0 * i for i in range(len(self.test_n))]
        self.test_a = data_a.drop(self.train_a.index)
        self.test_a = self.test_a.drop(self.val_a.index)
        self.test_a['target'] = [i**0 for i in range(len(self.test_a))]

        if self.only_normal == True:
            test = self.test_n

        else:    
            test = pd.concat([self.test_n,self.test_a], ignore_index=True)
        test = test.fillna(0)
        test = shuffle(test).reset_index(drop=True)
        targets = test['target']
        self.test_set_t = test
        test = test.drop(['target'],axis=1)
        return test, targets

if __name__=="__main__":
    # the parser
    parser = argparse.ArgumentParser(
                    prog='Data preprocesser',
                    description='This program preprocesses the data according to a couple of different options',
                    epilog='Text at the bottom of help')

    parser.add_argument('filename',metavar= '<filename - normal dataset>')           # positional argument
    parser.add_argument('filename1',metavar= '<filename - abnormal dataset>')
    parser.add_argument('savefile', metavar= '<savefilename1 - to save the prerocessed normal dataset>')
    
    parser.add_argument('-he', '--health',help='remove health calls from dataset', dest='health', default=False, action='store_true')      # option that takes a value
    parser.add_argument('-e', '--even', help='the create even dataset of normal and abnormal data (True or False)',default='True',action='store_true')
    parser.add_argument('-c','--cosine', help='use cosine similarity to remove features', default=False,action='store_true')
    parser.add_argument('-d','--data_remove', help='set of data to be removed',nargs=1, default=set(), type=set)
    parser.add_argument('-k','--to_keep', metavar='set of data to be kept',nargs=1, default=set(), type=set)
    parser.add_argument('-co','--continuous',metavar='list of continuous features', nargs=1, default=[], type=list)
    parser.add_argument('-n','--numerical', metavar='list of numerical features',nargs=1, default=[], type=list)
    parser.add_argument('savefile', metavar= '<savefilename2 - to save the prerocessed abnormal dataset>')
    
    interesting_to_keep = set(('flow_freq','user_agent','response_code','response_line','cache_control','content_type' ,'content_length','server','time','file_data','dst','src','src_p','dst_p','request_method','request_uri','request_uri_query','x_forwarded_for','user_agent','cookie','transfer_encoding','referer','authorization','authbasic'))
    data_remove = set(('_ws_expert', 'chat', '_ws_expert_message'))
    args = parser.parse_args()
    print("loading in the dataset..")
    data_n = pd.read_pickle(args.filename).reset_index()
    data_a = pd.read_pickle(args.filename1).reset_index()
    
    print("starting preprocessing..")
    Data_p = Data_Preprocess(data_n, data_a)
    flows_a = APIflows2(Data_p.data[1])
    flows_n =  APIflows2(Data_p.data[0])
    flows = [flows_n,flows_a]
    Data_p.Adding_flow_feature(Data_p.data, flows)
    data = Data_p.create_dataset(interesting_to_keep, data_remove, args.health, args.even, args.cosine,args.continuous,args.numerical)
    # filenames = ['../../Dataset/Mixed/final_normal_dataset_with_health.pkl','../../Dataset/Mixed/final_abnormal_dataset_with_health.pkl']
    filenames = ['../../Dataset/TheLastOFUs/preprocessed_normal.pkl', '../../Dataset/TheLastOFUs/preprocessed_abnormal.pkl']
    print('Saving the files in', filenames)
    Data_p.save_dataset(filenames,data)


    