import numpy as np
import matplotlib.pyplot as plt
from numpy import genfromtxt
import pandas as pd
import seaborn as sns
from tabulate import tabulate 
# from texttable import Texttable
import pickle
import os
import random
from scipy.stats import rankdata, norm


from category_encoders import *
from flows import *
from feature_encodings import *
from preprocessing import *
from visualising_dataset import *

# class create_visualisations():
def data_tabling(data):
    '''Displays a pandas dataframe that shows the number of different classes in each feature, 
    the average amount that the same feature is seen, the minimum amount that one of the classes of the feature is seen,
    and the maximum amount that the class of a feature is seen
    This gives us insight in which classes are used a lot within each feature'''
    max_n = []
    min_n = []
    avg_n = []
    classes_n = []
    total_n = []
    data = [data[: int(len(data)/2)], data[int(len(data)/2):]]
    
    for i in range(2):
        # the amount of times a feature class is present in the data
        feature_classes = [len(data[i][column].unique()) if len(data[i][column].unique()) != 0 else [0] for column in data[i].columns]
        feature_numbers = [data[i][column].value_counts() if len(data[i][column].value_counts()) != 0 else [0] for column in data[i].columns]

        max_n.append([max(x) for x in feature_numbers])
        min_n.append([min(x) for x in feature_numbers])
        avg_n.append([np.mean(x) for x in feature_numbers])
        classes_n.append([x for x in feature_classes])
        total_n.append([sum(x) for x in feature_numbers])
    
    names = ['Features','Max. cat normal', 'Min. cat. normal','Avg. cat. normal','Amount of Categories normal','Total calls normal','Max. cat. abnormal', 'Min. cat. abnormal','Avg. cat. abnormal','Amount of Categories abnormal','Total calls abnormal']
    
    columns = [[data[0].columns[i], max_n[0][i], min_n[0][i], avg_n[0][i], classes_n[0][i],total_n[0][i],max_n[1][i], min_n[1][i], avg_n[1][i], classes_n[1][i],total_n[1][i]] for i in range(len(data[0].columns))] 
    df = pd.DataFrame(columns, columns=names)

#     display(df)
    return(df)

def distribution(i,n,data_n,data_a):
    d1 = [len(data_n[col].unique()) for col in data_n.columns]
    d2 = [len(data_a[col].unique()) for col in data_a.columns]
    
    d1_med = mediann(d1)
    d2_med = mediann(d2)
    d1_1,d1_2,d1_3,d2_1,d2_2,d2_3 = split(d1,d2,d1_med,d2_med)
    data = [(d1_1,d2_1),(d1_2,d2_2),(d1_3,d2_3)]
    inx = [0,len(d1_1)-1, len(d1_1)+len(d1_2)]
    ind = [len(data[0][0]),len(d1_1)+len(d1_2)-1,len(d1)-1,len(d1_1)+len(d1_2)-1]
    
    for i in range(3):
        sns.set_style('darkgrid')
        sns.color_palette('pastel')
        X = np.arange(len(data_a.columns))
        fig = plt.figure(figsize=(12,6))
        ax = fig.add_axes([0,0,1,1])
        ax.barh(X[inx[i]:ind[i]] + 0.00,data[i][0],0.25, color= sns.color_palette('pastel')[0],label='normal')
        ax.barh(X[inx[i]:ind[i]] + 0.25, data[i][1], 0.25,color= sns.color_palette('pastel')[2],label='anomaly')
        ax.set_yticks(X[inx[i]:ind[i]], data_n.columns[inx[i]:ind[i]])
        ax.legend(title='Target')
        plt.xlabel('Number of categories')
        plt.ylabel('Features')
        plt.title('Number of categories per feature')
    
def mediann(lst):
    n = len(lst)
    s = sorted(lst)
    return np.median(lst)

def split(d1,d2,d1_med,d2_med):
    d1_1 = d1_2 = d1_3 = d2_1 = d2_2 = d2_3 = []
    if len(d1) > len(d2):
        index = d2
    else:
        index = d1
    for i in range(len(index)):
        if d1[i] <= d2_med and d2[i] <= d2_med:
            d1_1.append(d1[i])
            d2_1.append(d2[i])
        
        elif d1[i] <= np.mean(d1) and d2[i] <= np.mean(d1):
            d1_3.append(d1[i])
            d2_3.append(d2[i])
        else:
            d1_2.append(d1[i])
            d2_2.append(d2[i])
    return d1_1,d1_2,d1_3,d2_1,d2_2,d2_3


def create_sankey(flows,n,lab,option='default'):
    '''creates sankey diagram according to option for flow
        *** input***
            flows - the object containing the dicts and lists of flows/paths
            n - the number of flows  you want visualised
            lab - the labels for each flow
            option - the option of what needs to be visualised
            
        *** Options ***
            longest - The longest n paths users have taken
            shortest - The shortest n paths users have taken
            most - The n paths users take most offten
            least - The n paths users take least often
            defualt - Visualising the most seen api calls made from on point to another
        '''
    if option == 'longest':
        longest = flows.shortest
        longest.sort(key=lambda l: (len(l), l),reverse=True)
        plot_sankey(longest[:n], lab, flows.numbers,n)

    elif option == 'shortest':
        shortest = flows.shortest
        shortest.sort(key=lambda l: (len(l), l))
        plot_sankey(shortest[:n], lab, flows.numbers,n)
        
    elif option == 'most':
        flow_dict = dict(sorted(flows.numbers.items(), key=lambda x:x[1],reverse=True))
        plot_sankey(list(flow_dict.keys())[:n],lab, flows.numbers,n)
        
    elif option == 'least':
        flow_dict = dict(sorted(flows.numbers.items(), key=lambda x:x[1]))
        plot_sankey(list(flow_dict.keys())[:n], lab, flows.numbers,n)
        
    else:
        flow_dict = dict(sorted(flows.flowdict.items(), key=lambda x:x[1],reverse=True))
        plot_sankey(list(flow_dict.keys())[:n],lab, flow_dict,n)

# class Visualize():
def visualise_distribution(data_n,data_a, folder):
        
    data_n['target'] = 'normal'
    data_a['target'] = 'abnormal'

    # Concatenate the DataFrames
   
    combined_df = pd.concat([data_n, data_a])
    num_set = set(('content_length', 'time'))
    smallset = set(('response_code', 'response_line', 'request_method', 'x_forwarded_for', 'dst_p', 'cache_control','server','src','authbasic'))
    long_set = set(('src_p', 'request_uri_query','dst', 'request_uri')) #'file_data'
    medium_set = set(('user_agent','content_type','referer','authorization', 'cookie'))
    for column in combined_df.columns:
        if column == 'target':
            pass
        elif column in smallset:
            combined_df[column] = combined_df[column].astype(str)
        elif column in medium_set:
            combined_df[column] = combined_df[column].astype(str).str[:6]
        elif column in num_set:
            combined_df[column] = combined_df[column].astype(float)
        else:
            combined_df[column] = combined_df[column].astype(str).str[:10]

    sety = smallset | medium_set | num_set 
    fig, axs = plt.subplots(4,4, figsize=(20,20))
    count=0
    for j in range(4):
        for i in range(4):
            # if count < len(sety):
            at = sns.histplot(data=combined_df, x=list(sety)[count], hue='target',kde=True,  color=sns.color_palette('pastel')[0], ax=axs[i,j])
            for k, cont in enumerate(at.containers):
                if k %2 == 0:
                    at.bar_label(cont,label_type='edge',color='red')
                else:
                    at.bar_label(cont,label_type='edge',color='black')

                    # if k+1 == len(at.containers):
                    #     break
                    # for l,label in enumerate(at.bar_label(cont)):

                    #     if at.bar_label(cont)[l].__getattribute__('_text') > at.bar_label(at.containers[k+1])[l].__getattribute__('_text'):
                    #         at.bar_label(cont[l],label_type='edge')

                    #     else:
                    #         at.bar_label(cont[l],label_type='center')


            plt.ylabel('Count')
            count+=1

            # else:
            #     xmax = [ 1000,0.5]
            #     sns.histplot(data=combined_df, x=num_set[count-len(sety)],hue='target',kde=True, palette='pastel', ax=axs[i,j])
            #     plt.xlim(0, xmax[count-len(sety)])
            #     plt.ylim(0,max(combined_df[num_set[count-len(sety)]].value_counts().to_dict().values()))
                    
        fig.suptitle('Distribution of categories for each feature')
        fig.savefig(folder + 'distribution of amount of each category in each feature'+'.png')
        # plt.show()
    fig, axs = plt.subplots(1,2, figsize=(10,5))
    for i in range(2):
        xmax = [ 1000,0.5]
        sns.histplot(data=combined_df, x=list(num_set)[i],hue='target',kde=True, palette='pastel', ax=axs[i])
        plt.xlim(0, xmax[i])
        plt.ylim(0,max(combined_df[list(num_set)[i]].value_counts().to_dict().values()))
    fig.legend(['normal','abnormal'])
    fig.suptitle('Distribution of categories for each feature')
    fig.savefig(folder + 'distribution of amount of each category in each feature'+'timeandcont'+'.png')

    fig, axs = plt.subplots(3,2, figsize=(20,60))
    count = 0
    for i in range(3):
        for j in range(2):
            if count >= len(list(long_set)):
                pass
            else:
                sns.histplot(data=combined_df, y=list(long_set)[count],hue='target',kde=True, palette='pastel', ax=axs[i,j])
                count+= 1
        # plt.xlim(0, xmax[i])
        # plt.ylim(0,max(combined_df[num_set[i]].value_counts().to_dict().values()))
    fig.legend(['normal','abnormal'])
    fig.suptitle('Distribution of categories for each feature')
    fig.savefig('distribution of amount of each category in each feature'+'longsets'+'.png')        


def visualizing_overlap_and_NANS(data_n,data_a):
    
    df = {}

    for col in data_n.columns:
        vals = [sum(data_n[col].isna()),len(data_n[col]) - sum(data_n[col].isna()), len(data_n[col])]
        
        if col in data_a.columns:     
            df[col] = vals
        else:
            df[col] = vals + [0,0,0]
    for col in data_a.columns:
        vals = [sum(data_a[col].isna()),len(data_a[col]) - sum(data_a[col].isna()), len(data_a[col])]
        
        if col not in df.keys():
            df[col] = [0,0,0] + vals
        else:
            df[col] += vals
    
    df1 =df
    df = pd.DataFrame(df,index=['NAN N','feat N','total N','NAN A','feat A','total A']).T
    display(df[30:])
    plotbar(df.values[:,1],df.values[:,0],df.values[:,4],df.values[:,3],df1.keys(),size=[12,24])
    
def visualise_number_of_categories_and_overlap(train_set,val_set,test_set, savefolder,size=[12,24]):
    col_df_1 = {}
    col_df_2 = {}
    for column in train_set.columns:
        df_n = train_set[column].where(train_set['target'] == 0).dropna().value_counts().to_dict()
        df_a = train_set[column].where(train_set['target'] == 1).dropna().value_counts().to_dict()
        overlap =list(set(df_n.keys())& set(df_a.keys()))
        overlap = {x: df_n[x] + df_a[x] for x  in overlap}
        names = ['abnormal','normal','overlap']
        if len(df_n.keys()) > 100 or len(df_a.keys()) > 100:
            col_df_1[column] = [len(df_n.keys()),len(df_a.keys()), len(overlap.values(),)]
        else:
            col_df_2[column] = [len(df_n.keys()),len(df_a.keys()), len(overlap.values(),)]


    col_df_11 = pd.DataFrame(col_df_1,columns=col_df_1.keys(),index=['normal','abnormal','overlap']).T
    col_df_22 = pd.DataFrame(col_df_2,columns=col_df_2.keys(),index=['normal','abnormal','overlap']).T

    print(col_df_1)
    plotbar1(col_df_11.values[:,0],col_df_11.values[:,1],col_df_11.values[:,2],col_df_11.values[:,2],col_df_1.keys(),'category_distribution_first',size=[12,34])
    plotbar1(col_df_22.values[:,0],col_df_22.values[:,1],col_df_22.values[:,2],col_df_22.values[:,2],col_df_2.keys(),'category_distribution_second',size=[12,34])

    # sns.set_style('darkgrid')
    # sns.color_palette('pastel')
    # X = np.arange(len(train_set.columns))
    # fig = plt.figure(figsize=size)
    # ax = fig.add_axes([0,0,1,1])
    # ax.barh(X -0.2,col_df.values[:,0],0.2, color= sns.color_palette('pastel')[1],label='normal')
    # ax.barh(X + 0.0,col_df.values[:,1], 0.2,color= sns.color_palette('pastel')[5],label='abnormal')
    # ax.barh(X + 0.2,col_df.values[:,2],0.2, color= sns.color_palette('pastel')[3],label='overlap')
    # ax.barh(X + 0.2,col_df.values[:,2],0.2, color= sns.color_palette('pastel')[3],label='overlap')
    # print(train_set.columns)
    # ax.set_yticks(X, train_set.columns)
    # ax.set_xticks(X)
    # ax.legend(title='legend')
    # plt.xlabel('Number of categories per feature for normal, abnormal and overlap')
    # plt.ylabel('Features')
    # plt.title('Number of categories per feature')
    # plt.savefig(savefolder+"/distribution of categories.png")
    # plt.clf

def plotbar1(a,b,c,d,names,filename,size=[12,6]):
    sns.set_style('darkgrid')
    sns.color_palette('pastel')
    X = np.arange(len(a))
    fig, ax = plt.subplots(figsize=(24, 12))
    # ax = fig.add_axes([0,0,1,1])
    plt.barh(X -0.2,a,0.2, color= sns.color_palette('pastel')[1],label='normal')
    plt.barh(X + 0.0,b, 0.2,color= sns.color_palette('pastel')[5],label='abnormal')
    plt.barh(X + 0.2,c,0.2, color= sns.color_palette('pastel')[3],label='overlap')
    plt.yticks(X, names)
    plt.legend(title='Legend')
    # ax.set(xlabel='Score', ylabel='Iterations', title='Training Curve')
    plt.xlabel('Number of categories')
    plt.ylabel('Features')
    plt.title('Number of categories per feature')  
    fig.savefig(filename+'.png')
    plt.clf()
    # plt.show()
        
def plot_sankey(s,lab,flow_dict,n):
    '''Plot the sankey diagram
    *** Input ***
        s - the target for each vertex
        lab - the label for each node
        flow_dict - the dictionary with paths containing edges and values
        n - the number of paths
    '''

    color_pal = sns.color_palette("Spectral",n).as_hex()
    
    # sort so that the sankey diagram is visualised in the right order
    s.sort()
    # if a list is used, some changes are made to visualise the paths
    if type(s[0]) is list:
        v = [[flow_dict[tuple(x)]] * len(x) for x in s]
        v1 = []
        s1 = []
        for i in range(len(s)):
            s1 = s1 + s[i]
            v1 = v1 + v[i]
        s =s1
        v =v1
    
    # this is used when there is not path just edges
    else:
        v = [flow_dict[x] for x in s]

    # creating label names instead of numbers
    l = ['client'] + [lab[x][:12] for x in range(1,len(lab))]
    
    # the dictionary is filled with tuples, so again some changes need to be added to representation
    if type(s[0][0]) is tuple:
        s1 = []
        for i in range(len(s)):
            s1 = s1 + list(s[i])
        s = s1
    
    # creating the figure
    fig = go.Figure(go.Sankey(
        arrangement='snap',
        node=dict(
            label = l,
            line = dict(color = "black", width = 0.5),
            pad=15,
            thickness=20,
        ),
        link=dict(
            source = list(np.array(s)[:,0]) ,
            target = list(np.array(s)[:,1]),
            value= v,
        )
    ))

    fig.show()

if __name__=="__main__":
        # the parser
    parser = argparse.ArgumentParser(
                    prog='Data Visualisation',
                    description='',
                    epilog='Text at the bottom of help')

    parser.add_argument('filename',metavar= 'filename of normal dataset')           # positional argument
    parser.add_argument('filename1',metavar= 'filename of abnormal dataset')
    parser.add_argument('savefolder', metavar= 'the file to save the prerocessed dataset')
    args = parser.parse_args()

    # load the preprocessed dataset
    data_n = pd.read_pickle(args.filename)
    data_a = pd.read_pickle(args.filename1)
    
    # categorical and numerical data defined
    categorical_feats = ['user_agent','response_line','cache_control', 'content_length','server','file_data','dst','src','src_p','dst_p','request_method','request_uri','request_uri_query','x_forwarded_for','user_agent','cookie','transfer_encoding','referer','authorization','authbasic','content_type','response_code']
    numerical = ['time']

    # create data preprocessing object
    data_preprocessor = Data_Preprocess(data_n,data_a)

    # change the values to string and float formats
    data_n = data_preprocessor.change_values(data_n,numerical,categorical_feats)
    data_a = data_preprocessor.change_values(data_a,numerical,categorical_feats)
    data = [data_n,data_a]
    # num_dict = data_n['request_uri'].to_dict()
    # create_sankey(flows_n,20, num_dict,'default')
    # num_dict2 = data_a['request_uri'].to_dict()
    # create_sankey(flows_a,20, num_dict2,'default')
    # create_sankey(flows_n,1, num_dict,'longest')
    # create_sankey(flows_a,1, num_dict2,'longest')
    # create_sankey(flows_n,7, num_dict,'shortest')
    # create_sankey(flows_a,7, num_dict2,'shortest')
    # create_sankey(flows_n,50, num_dict,'most')
    # create_sankey(flows_a,20, num_dict2,'most')
    # create_sankey(flows_n,50, num_dict,'least')
    # create_sankey(flows_a,50, num_dict2,'least')
    encoder_obj = Encoders()
    encoders = encoder_obj.encoders
    filter_obj = Filters()

    splitter = Train_Val_Test_split()
    # X_n = encoder_obj.choose_encoding(data[0],'cat')
    # X_a = encoder_obj.choose_encoding(data[1],'cat')
    splitter.split_dataset([data_n,data_a])

    # visualise_number_of_categories_and_overlap(splitter.train_set_t,splitter.val_set_t,splitter.test_set_t, args.savefolder)
    visualise_distribution(splitter.train_set.where(splitter.train_set_t['target'] == 0).dropna(),splitter.train_set.where(splitter.train_set_t['target'] == 1).dropna(), args.savefolder)

