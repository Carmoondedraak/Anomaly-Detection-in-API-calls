import numpy as np
import matplotlib.pyplot as plt
from numpy import genfromtxt
import pandas as pd
import seaborn as sns
from tabulate import tabulate 
from texttable import Texttable
import pickle
import os
import random
from scipy.stats import rankdata, norm

class create_visualisations():
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

class Visualize():
    def visualise_distribution(data_n,data_a):
        for m in range(6):
            fig, axs = plt.subplots(3,3, figsize=(10,10))
            count=[0,9,18,27,36,45][m]
            for j in range(3):
                for i in range(3):
                    sns.histplot(data_n[data_n.columns[count]].value_counts(),kde=True, color=sns.color_palette('pastel')[0], ax=axs[i,j],label='normal',legend=True)
                    sns.histplot(data_a[data_a.columns[count]].value_counts(),kde=True,   color=sns.color_palette('pastel')[2], ax=axs[i,j],label='abnormal',legend=True)
                    count+=1

            fig.suptitle('Distribution of categories for each feature')
            fig.legend(['normal','abnormal'])
            plt.show()
        visualise_distribution(data_n,data_a)

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
        
    def plotbar(a,b,c,d,names,size=[12,6]):
        sns.set_style('darkgrid')
        sns.color_palette('pastel')
        X = np.arange(len(a))
        fig = plt.figure(figsize=size)
        ax = fig.add_axes([0,0,1,1])
        ax.barh(X -0.2,a,0.2, color= sns.color_palette('pastel')[1],label='feat N')
        ax.barh(X + 0.0,b, 0.2,color= sns.color_palette('pastel')[5],label='NAN N')
        ax.barh(X + 0.2,c,0.2, color= sns.color_palette('pastel')[3],label='feat A')
        ax.barh(X + 0.4,d, 0.2,color= sns.color_palette('pastel')[4],label='NAN A')
        ax.set_yticks(X, names)
        ax.legend(title='Target')
        plt.xlabel('Number of categories')
        plt.ylabel('Features')
        plt.title('Number of categories per feature')  
            
    def plot_sankey(s,lab,flow_dict,n):
        '''Plot the sankey diagram
        *** Input ***
            s - the source for each vertex
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
    num_dict = data_n['request_uri'].to_dict()
    create_sankey(flows_n,20, num_dict,'default')
    num_dict2 = data_a['request_uri'].to_dict()
    create_sankey(flows_a,20, num_dict2,'default')
    create_sankey(flows_n,1, num_dict,'longest')
    create_sankey(flows_a,1, num_dict2,'longest')
    create_sankey(flows_n,7, num_dict,'shortest')
    create_sankey(flows_a,7, num_dict2,'shortest')
    create_sankey(flows_n,50, num_dict,'most')
    create_sankey(flows_a,20, num_dict2,'most')
    create_sankey(flows_n,50, num_dict,'least')
    create_sankey(flows_a,50, num_dict2,'least')