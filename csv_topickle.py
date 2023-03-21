import pandas as pd
import pickle
df = pd.read_csv('orderv2.json.csv')
#with open('data/dataframe_n.pkl','rb') as f:
#	dff = pickle.load(f)
# for i in range(1633):
#     df1 = pd.read_pickle('data/dataframe_{}'.format(i+1))
#     df = pd.concat([df,df1],ignore_index=True)

# df.to_pickle('data/dataframe_first_try')
csv = df.to_pickle('data/anamolies.pkl')

