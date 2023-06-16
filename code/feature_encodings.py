from category_encoders import *

class feature_encoders()
    def __init__():
        pass

    def one_hot(data):
        '''encode full dataframe in one hot encoding'''
        one_hot_enc = pd.get_dummies(data)
        return one_hot_enc

    def hashing(data):
        '''encode full '''
        enc = HashingEncoder().fit(data)
        numeric_dataset = enc.transform(data)
        return numeric_dataset

    def WoE_encoding(data, not_count):
        '''weight of evidence encoding'''
        
        df = {}
        for col in data.columns:
            # calculate the WoE of each category of each feature, leave some of the data out, if it is not existent in both.
            if col not in not_count:
                woe_iv_dict = {}
                
                # create multi-index dataframe to better handle the indexing for this.
                feat_num2 =  data.groupby(col,as_index=False)['target'].value_counts()
                s = pd.Series(list(feat_num2['count']), index= pd.MultiIndex.from_tuples(list(zip(*[list(feat_num2['target']),list(feat_num2[col])])), names=["first", "second"]))
                dicty = dict(s)

                for cat in feat_num2[col]:
                    # check if both normal and anomalous data is present, if not fill in 0 for this.
                    if (1,cat) not in dicty or (0,cat) not in dicty:
                        if (1,cat) in dicty:
                            woe, IV = WoE(s.loc[1,cat],0,s[1].sum(),s[0].sum())
                        elif (0, cat) in dicty:
                            woe, IV = WoE(0,s.loc[0,cat],s[1].sum(),s[0].sum())
                    else:
                        woe, IV = WoE(s.loc[1,cat],s.loc[0,cat],s[1].sum(),s[0].sum())
                        
                    woe_iv_dict[cat] = [woe,IV]

                    df['total_'+str(col)] = [sum([x[0] for x in list(woe_iv_dict.values())]), sum([x[1] for x in list(woe_iv_dict.values())])]    
            df1 = pd.DataFrame.from_dict(woe_iv_dict)
        df = pd.DataFrame.from_dict(df,orient='index',columns=['total_WoE','total_IV'])
        display(df)

        return df
            

    def WoE(x1,x2,tot1,tot2):
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


    def freq(data):
        '''encode full dataframe in frequency encoding'''
        enc = CountEncoder().fit(data)
        numeric_dataset = enc.transform(data)
        return numeric_dataset


    def categorical_encoding(df):
        '''encode full dataframe as categorical encoding'''
        
        df = copy.deepcopy(df)
        for col in df.columns:
            df[col] = pd.factorize(df[col])[0] + 1
        return df
        
if __name__=="__main__":
    not_count = ['authorization', 'authbasic', 'location', 'target']
    woe_df = WoE_encoding(data, not_count)
    freq(data)