import pandas as pd
import pickle
df = pd.read_pickle('data/dataframe_new.pkl')
#with open('data/dataframe_n.pkl','rb') as f:
#	dff = pickle.load(f)
# for i in range(1633):
#     df1 = pd.read_pickle('data/dataframe_{}'.format(i+1))
#     df = pd.concat([df,df1],ignore_index=True)

# df.to_pickle('data/dataframe_first_try')
csv = df.to_csv('data/dataframe_new.csv',index=False)
print(df['request time'])
print(df['type'])
if 'DELETE' in df['type'].values:
   print('yes')
if 'GET' in df['type'].values:
   print('does thiswork')

