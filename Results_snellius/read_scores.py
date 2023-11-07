import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
filenames = ['Results_fast_fs/', 'Results_fast_fs_hash/', 'Results_fast_fs_woe/','Results1/']

def generate_csv(filenames):
    df = pd.read_pickle(filenames[0] + 'scores.pkl')
    new_df = pd.DataFrame(columns=df.columns, index=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16])
    ind = 0


    k = []
    for file in filenames:
        df = pd.read_pickle(file + 'scores.pkl')
        features = []
        for i in range(len(df)-1):
            if df['filter/model'].loc[i] == df['filter/model'].loc[i+1]:
                features.append(df['feature_names'].loc[i])
            else:
                if len(new_df) == 0: 
                    new_df =  pd.DataFrame(df.loc[i],columns=df.columns)
                else:
                    # pd.concat = [new_df, df.loc[i]]
                    new_df.loc[ind] = df.loc[i]
                features.append(df['feature_names'].loc[i])    
                # new_df.loc[ind]['feature_names'] = str(features)
                k.append(len(features))
                ind += 1

                features =[]

    
    new_df = new_df.fillna(0)
    k = k + [0 for i in range(len(new_df)- len(k))]
    new_df['k'] = k
    new_df =new_df.round(3)
    new_df.to_csv('all_scores_rounded.csv')
    return new_df

def feature_hist(filenames):
    df_f = pd.read_pickle('../data/synthetic_data2/train.pkl')
    features = df_f.columns
    feature_dict = {k:0 for k in features}
    print(feature_dict)

    df = pd.read_pickle(filenames[0] + 'scores.pkl')

    for file in filenames:
        df = pd.read_pickle(file + 'scores.pkl')
        for i in range(len(df)):
            feat = df.loc[i]['feature_names']
            if feat in feature_dict:
                feature_dict[feat] += 1
    print(feature_dict)
    # df_ff = pd.DataFrame.from_dict(feature_dict,orient='index', columns=[feature_dict.keys])
    # print(df_ff)
    plot = sns.barplot(x=list(feature_dict.keys()),y=list(feature_dict.values()))
    # for item in plot.get_xticklabels():
    #     item.set_rotation(45)
    plt.xticks(rotation=45,horizontalalignment='right')
    plt.tight_layout()
    # plt.show()
    plt.savefig('dsitribution_of_fs.png')
# feature_hist(filenames)       

df = pd.read_csv('~/Downloads/tableConvert.com_58pgw0.csv')
plot = sns.barplot(x=list(feature_dict.keys()),y=list(feature_dict.values()))
# for item in plot.get_xticklabels():
#     item.set_rotation(45)
plt.xticks(rotation=45,horizontalalignment='right')
plt.tight_layout()
# plt.show()
plt.savefig('dsitribution_of_fs.png')