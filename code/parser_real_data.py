#parsing
import pandas as pd
import json
from preprocessing import *
from feature_encodings import *

df = pd.read_excel(r'~/Downloads/All-Messages-search-result.xlsx')

def santizite(mess):
    for i,m in enumerate(mess):

        if ']' in m:
            m = m.strip(']')
        if 'torii-request-id=' in m:
            m = m.strip('torii-request-id=')
        if '"' in m:
            mess[i] = m.strip('"')
        if '[' in m:
            mess[i] = m.strip('[')

    if '' in mess:
        mess.remove('')
    return mess

def remove_missing(mes):
    j=0
    for n,c in enumerate(mes):
        if c == '-' and n==len(mes)-1 or c=='-' and n==len(mes) or n-1==len(mes) and c=='-':
            if j==0:
                pass
            else:
                mes = mes[:n-1]+ '0' + mes[n+1:]
            j+=1
        elif c == '-' and mes[n+1] == ' ' :
            if j==0:
                pass
            else:
                mes = mes[:n-1]+ '0' + mes[n+1:]
            j+=1
    return mes

def split_string(mes):
    mess = mes.split(' ')
    mess = mess[0].split('-') + mess[1:]
    mess = mess[:1] + mess[1].split('[') + mess[2:]
    return mess

def main(df):
    new_list =[]
    j = 0
    for i,mes in enumerate(df['message']):
        
        if len(mes) > 36:
            if mes[0] == '{':

                mess = json.loads(mes)
                headers = mess['headers']
                mess = mess| headers
                del mess['headers']

                if j == 0:
                    df2 = pd.DataFrame.from_dict(mess)
                    j+=1
                else:
                    df3 = pd.DataFrame.from_dict(mess)
                    df2 = pd.concat([df2, df3], ignore_index=True)
                
            else:

                mess = split_string(mes)
                mess = santizite(mess)
                mess_user = " ".join(mess[11:-1])

                mess = mess[:11] + [mess_user] + mess[-1:]
                new_list.append(mess)

    df1 = pd.DataFrame(new_list, columns = ['remote_addr','some', 'remote_user', 'Date','seconds', 'method','url','version', 'status','Content-Length', 'referer','user_agent','torii-request-id'])  
    df = pd.concat([df1,df2],ignore_index=True)

    for col in df.columns:
        for i,j in enumerate(df[col]):
            if j == '-':
                df[col][i] = 0
    # some specific pre-processing
    df['referer'] = df['referer'].map(str)
    for n in range(len(df['status'])):
        if  df['status'][n] == '304 Not Modified':
            df['status'][n] = '304'
        if df['status'][n] == '200 OK':
            df['status'][n] = '200'
    for n in range(len(df['referer'])):
        if df['referer'][n][0] =='$':
            df['referer'][n] = df['referer'][n][1:]


    for n in range(len(df['user_agent'])):
        if type(df['user_agent'][n]) == str:
            if len(df['user_agent'][n]):
                if df['user_agent'][n][0] =='$':
                    df['user_agent'][n] = df['user_agent'][n][1:]

    df.to_pickle("../data/real_world_dataset.pkl")  

def preprocess(data,Data_p,filename):
    data = Data_p.create_dataset(data_remove = ('some','Date','time','Name vulnerability'),health=False,even=False)
    print(data)
    Data_p.save_dataset(filename,data[0],flag=True)

class Train_Val_Test_split_Real():
    '''splits the data into train, validation and test'''

    def __init__(self,percentages = '0.70:0.20:0.10', only_normal = False):
        '''split the data into 70-20-10'''
        self.percentage = percentages
        self.only_normal = only_normal

    def split_dataset(self, data): 
        print('lenght of total data', len(data))
        self.train_set, self.train_targets = self.train(data)
        self.val_set, self.val_targets = self.val(data)
        self.test_set, self.test_targets = self.test(data)
        print('Length of train data:', len(self.train_set), sum(self.train_targets),' \n length of validation data', len(self.val_set), sum(self.val_targets), '\n length of the test data', len(self.test_set),sum(self.test_targets))

    def train(self, data):
        perc = float(self.percentage.split(':')[0])
        self.train = data.sample(frac=perc)
        self.train['target'] = [0 * i for i in range(len(self.train))]
        
        train = self.train
        train = train.fillna(0)
        train = shuffle(train).reset_index(drop=True)
        targets = train['target']
        self.train_set_t = train
        train = train.drop(['target'],axis=1)
        return train, targets

    def val(self, data):
        perc = float(self.percentage.split(':')[1])
       
        self.val = data.drop(self.train.index)
        perc = ((len(data) * perc) /len(self.val))
        print(perc, len(self.val))
        self.val = self.val.sample(frac=perc)
        self.val['target'] = [0 * i for i in range(len(self.val))]

        validation = self.val
        validation = validation.fillna(0)
        validation = shuffle(validation).reset_index(drop=True)
        targets = validation['target']
        self.val_set_t = validation
        validation = validation.drop(['target'],axis=1)
        return validation,targets 

    def test(self, data):
        self.test = data.drop(self.train.index)
        self.test = self.test.drop(self.val.index)
        self.test['target'] = [0 * i for i in range(len(self.test))]

        test = self.test
        test = test.fillna(0)
        test = shuffle(test).reset_index(drop=True)
        targets = test['target']
        self.test_set_t = test
        test = test.drop(['target'],axis=1)
        return test, targets

# main(df)

# file = '../data/real_world_dataset.pkl'
# data = pd.read_pickle(file)
# Data_p = Data_Preprocess([data])

# abnormal_file = '../data/real_data/anomalous_real_dataset.csv'


# preprocess(file, Data_p,'../data/preprocessed_real_world_dataset.pkl')
# abnormal = pd.read_csv(abnormal_file, sep=';').fillna(0)
# Data_p = Data_Preprocess([abnormal])
# preprocess(abnormal_file, Data_p,'../data/preprocessed_abnormal_real_world_dataset.pkl')

filenames = ['../data/train_real.pkl', '../data/val_real.pkl','../data/test_real.pkl', ]
target_names = ['../data/train_real_targets.pkl', '../data/val_real_targets.pkl','../data/test_real_targets.pkl']


# dataset 
data1 = pd.read_pickle('../data/preprocessed_real_world_dataset.pkl')
data2 = pd.read_pickle('../data/preprocessed_abnormal_real_world_dataset.pkl')
encoder_obj = Encoders()
encoders = encoder_obj.encoders

# splitter = Train_Val_Test_split_Real()

encoder = 'cat'


data = encoder_obj.choose_encoding(data,encoder)
Data_p.save_dataset('../data/real_data/abnormal_test_real.pkl', data,flag=True)
print(data)
# df = read_pickle('')
# splitter.split_dataset(data)
# train = splitter.train_set
# train_targets = splitter.train_targets
# val = splitter.val_set
# val_targets = splitter.val_targets
# test = splitter.test_set
# test_targets = splitter.test_targets

# Data_p.save_dataset(filenames[0],train,flag=True)
# Data_p.save_dataset(target_names[0],train_targets,flag=True)

# Data_p.save_dataset(filenames[1],val,flag=True)
# Data_p.save_dataset(target_names[1], val_targets,flag=True)

# Data_p.save_dataset(filenames[2],test,flag=True)
# Data_p.save_dataset(target_names[2], test_targets,flag=True)

