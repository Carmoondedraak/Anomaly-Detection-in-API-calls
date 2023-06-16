import copy
import math
import argparse
import pandas as pd

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
    def __init__(self, data_n, data_a, health=True, even=True, cosine = False, to_keep=set(), data_remove=set(),continuous=[],numerical=[]):
        self.to_keep = to_keep
        self.data_remove = data_remove
        self.data_n = data_n
        self.data_a = data_a
        self.data = [data_n,data_a]
        self.continuous = continuous
        self.numerical = numerical 
        
        self.specific_preprocessing
        if len(self.to_keep) > 0:
            self.remove_specific_data
        if len(self.data_remove) > 0:
            self.remove_unessecary_data
        if health == True:
            self.remove_health_calls
        if even == True:
            self.even_dataset
        self.change_values
        
        
    def remove_unessecary_data(self):
        '''remove data that has no changing values or needs to be removed'''

        for i in range(len(self.data)):
            self.data[i] = self.data[i].fillna(0)

            for col in self.data[i].columns:
                if col in self.data_remove or len(self.data[i][col].value_counts()) == 1:
                    print('dataset', i, 'removed', col,'with only',len(self.data[i][col].value_counts()), 'specific values')
                    self.data[i].pop(col)



    def even_dataset(self):
        '''create even datasets and remove columns that are not present in either one'''
        if len(self.data_n) > len(self.data_a):
            self.data_n = self.data_n.sample(n=len(self.data_a))

        else:
            self.data_a = self.data_a.sample(n=len(data_n))


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
        print(removed)
        return data


    def specific_preprocessing(self):
        '''remove features specifically (only for this dataset useful)'''
        for i in range(2):
            data_p_n = copy.deepcopy(self.data)
            data_p_n.cookie.fillna(data_p_n.set_cookie, inplace=True)

            for i in range(len(self.data['response_line'])):
                if data_p_n['response_line'][i][0] != 'x':
                    data_p_n['response_line'][i] = 0
        self.data[i] = data_p_n

    def remove_specific_data(self):
        ''' removes all column but a specific set that it is to keep '''

        for i in range(2):
            for col in self.data[i].columns:
                if col not in self.to_keep:
                    self.data[i].pop(col)
        self.data =  [self.data[0], self.data[1]]


    def change_values(self, continuous, categorical):
        '''changes the values from type pyshark field to float or str'''

        print('cont',self.continuous,'cat',self.categorical)
        for i in range(2):
            for col in self.data[i].columns:
                if col in self.continuous: 
                    self.data[i][col] = self.data[i][col].astype('float')
                    print('string',col)
                elif col in self.categorical:
                    print('num',col)
                    self.data[i][col] = self.data[i][col].astype('str')

    def remove_health_calls(self):
        '''removes the health calls that are made within  the kubernetes environment'''

        data_n1 = copy.deepcopy(self.data_n)
        data_a1 = copy.deepcopy(self.data_a)
        data_n2 = data_n1.where(data_n1['user_agent'] != 'kube-probe/1.25')
        data_a2 =  data_a1.where(data_a1['user_agent'] != 'kube-probe/1.25')
        data_n2 = data_n2.dropna()
        data_a2 = data_a2.dropna()
        display(data_n2)
        display(data_a2)
    
if __name__=="__main__":
    # the parser
    parser = argparse.ArgumentParser(
                    prog='Data preprocesser',
                    description='This program preprocesses the data according to a couple of different options',
                    epilog='Text at the bottom of help')

    parser.add_argument('filename',metavar= 'filename of normal dataset')           # positional argument
    parser.add_argument('filename1',metavar= 'filename of abnormal dataset')
    parser.add_argument('savefile', metavar= 'the file to save the prerocessed dataset')
    
    parser.add_argument('-he', '--health',help='remove health calls from dataset', dest='health', default=False, action='store_true')      # option that takes a value
    parser.add_argument('-e', '--even', help='the create even dataset of normal and abnormal data (True or False)',default='False',action='store_true')
    parser.add_argument('-c','--cosine', help='use cosine similarity to remove features', default=False,action='store_true')
    parser.add_argument('-d','--data_remove', help='set of data to be removed',nargs=1, default=set(), type=set)
    parser.add_argument('-k','--to_keep', metavar='set of data to be kept',nargs=1, default=set(), type=set)
    parser.add_argument('-co','--continuous',metavar='list of continuous features', nargs=1, default=[], type=list)
    parser.add_argument('-n','--numerical', metavar='list of numerical features',nargs=1, default=[], type=list)
    parser.add_argument('savefile', metavar= 'the file to save the prerocessed dataset')
    
    args = parser.parse_args()
    print("loading in the dataset..")
    data_n = pd.read_pickle(args.filename)
    data_a = pd.read_pickle(args.filename1)

    print("starting preprocessing..")
    Data_p = Data_Preprocess(data_n, data_a, args.health, args.even, args.cosine, args.to_keep, args.data_remove,args.continuous,args.numerical)
    

