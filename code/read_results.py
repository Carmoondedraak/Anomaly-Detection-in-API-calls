import pandas as pd

df = pd.read_pickle('../Results_snellius/Results1/scores.pkl')
df.to_csv('../Results_snellius/Results1/scores.csv')
# df2 = pd.read_pickle('../Results_snellius/Results1/choi_lr_tuneresults.pkl')
# print(df2.columns)
df = pd.read_pickle('../../Dataset/TheLastOFUs/preprocessed_normal1.pkl')
print(df.columns)