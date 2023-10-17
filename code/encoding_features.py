from category_encoders import *
import pandas as pd
import copy


from category_encoders import *
from flows import *
from feature_encodings import *
from preprocessing import *
from visualising_dataset import *
class Encoders():
    def __init__(self):
        self.encoders = ['cat','one_hot', 'woe', 'freq']
        
    def choose_encoding(self, data, name):
        target = data['target']
        data = data.drop(columns='target')
        if name == 'one_hot':   
            n_data = self.one_hot(data)
        elif name == 'hash':
            n_data = self.hashing(data)
        elif name == 'woe':
            n_data = self.WoE_encoding(data,['authorization', 'authbasic', 'location', 'target'],'target')
        elif name == 'freq':
            n_data = self.freq(data)
        elif name == 'cat':
            n_data = self.categorical_encoding(data)
        n_data['target'] = target
        return n_data
            
    def one_hot(self, data):
        '''encode full dataframe in one hot encoding'''
        one_hot_enc = pd.get_dummies(data)
        return one_hot_enc

    def hashing(self, data):
        '''encode full '''
        enc = HashingEncoder().fit(data)
        numeric_dataset = enc.transform(data)
        return numeric_dataset

    def WoE_encoding(self, data, not_count,name):
        '''weight of evidence encoding'''

        df = {}
#         display(data)
        for col in data.columns:
            # calculate the WoE of each category of each feature, leave some of the data out, if it is not existent in both.
            if col not in not_count:
                woe_iv_dict = {}

                # create multi-index dataframe to better handle the indexing for this.
                feat_num2 =  data.groupby(col,as_index=False)[name].value_counts()
                s = pd.Series(list(feat_num2['count']), index= pd.MultiIndex.from_tuples(list(zip(*[list(feat_num2[name]),list(feat_num2[col])])), names=["first", "second"]))
                dicty = dict(s)

                for cat in feat_num2[col]:
                    # check if both normal and anomalous data is present, if not fill in 0 for this.
                    if (1,cat) not in dicty or (0,cat) not in dicty:
                        if (1,cat) in dicty:
                             woe, IV = self.WoE(s.loc[1,cat],0,s[1].sum(),s[0].sum())
                        elif (0, cat) in dicty:
                             woe, IV = self.WoE(0,s.loc[0,cat],s[1].sum(),s[0].sum())
                    else:
                        woe, IV = self.WoE(s.loc[1,cat],s.loc[0,cat],s[1].sum(),s[0].sum())

                    woe_iv_dict[cat] = [woe,IV]

                    df['total_'+str(col)] = [sum([x[0] for x in list(woe_iv_dict.values())]), sum([x[1] for x in list(woe_iv_dict.values())])]    
            df1 = pd.DataFrame.from_dict(woe_iv_dict)
        df = pd.DataFrame.from_dict(df,orient='index',columns=['total_WoE','total_IV'])
#         display(df)

        return df


    def WoE(self, x1,x2,tot1,tot2):
        '''calculate the WoE for the categories in a feature'''
        #change prop in second part as well

        if x1 == 0 or x2 ==0:
            prop_g = (x1 + 0.5) /tot1
            prop_b = (x2 + 0.5) /tot2  
        else:
            prop_g = x1 / tot1
            prop_b = x2 / tot2

        woe = np.log(prop_g / prop_b)

        IV = woe * (prop_g - prop_b)
        return woe, IV


    def freq(self, data):
        '''encode full dataframe in frequency encoding'''
        enc = CountEncoder().fit(data)
        numeric_dataset = enc.transform(data)
        return numeric_dataset


    def categorical_encoding(self, df):
        '''encode full dataframe as categorical encoding'''

        df = copy.deepcopy(df)
        for col in df.columns:
            df[col] = pd.factorize(df[col])[0] + 1
        return df

class Filters():
    def __init__(self):
        self.filters = ['choi','fisher','mutinf']
        
    def choose_filter(self, name, X, y, k):
        if name == 'choi':
            feats = self.chi_square(X,y,k)
        
        elif name == 'fisher':
            feats = self.fisher(X,y,k)
            
        elif name == 'mutinf':
            feats = self.mutual_information(X,y,k)

        return feats
    
    def chi_square(self, X,y,k):
        # Two features with highest chi-squared statistics are selected
        chi2_features = SelectKBest(chi2, k = k)
        X_kbest_features = chi2_features.fit_transform(X,y)
        feats = chi2_features.get_feature_names_out()
        return feats

    def fisher(self, X,Y,k):
        X = X.to_numpy()
        ranks = fisher_score.fisher_score(X,Y)
        whoop = np.argmax(ranks)
        feats = []
        for i in range(k):
            idx = np.argmax(ranks)
            ranks = np.delete(ranks, idx)
            feats.append(idx)
        return feats

    def fisher1(self,X,Y,k):
        mutual = SelectKBest(f_classif, k=k)
        X_kbest_features = mutual.fit_transform(X,Y)
        return mutual.get_feature_names_out()

    def mutual_information(self, X,Y,k):
        mutual = SelectKBest(mutual_info_classif, k=k)
        X_kbest_features = mutual.fit_transform(X,Y)
        return mutual.get_feature_names_out()

if __name__=="__main__":
    not_count = ['authorization', 'authbasic', 'location', 'target']
    woe_df = WoE_encoding(data, not_count)
    freq(data)