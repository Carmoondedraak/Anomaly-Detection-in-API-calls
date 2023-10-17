import pandas as pd
df = pd.read_pickle('../../Dataset/TheLastOFUs/preprocessed_normal.pkl')
df1 = pd.read_pickle('../../Dataset/TheLastOFUs/preprocessed_abnormal.pkl')

file = '../../Dataset/TheLastOFUs/preprocessed_normal1.pkl'
file2 = '../../Dataset/TheLastOFUs/preprocessed_abnormal1.pkl'

df = df.drop(columns=['src','dst'])
df1 = df1.drop(columns=['src','dst'])

df.to_pickle(file)
df1.to_pickle(file2)
print(df1.columns)