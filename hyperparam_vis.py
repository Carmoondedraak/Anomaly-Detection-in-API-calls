import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv('~/Downloads/hparams_table-5.csv')

df = df.rename({'vaegan':'Model'},axis='columns')
print(df)
for i in range(len(df)):
    if df['Model'].loc[i] == 0.0:
        df['Model'].loc[i] = 'Vaeganomaly'
    elif df['Model'].loc[i] == 1.0:
        df['Model'].loc[i] = 'Vaegan'
df_syn = df.where(df['data_dir'] == '/home/cveenker1/Anomaly-Detection-in-API-calls/data/synthetic_data2').dropna() 
df_rl = df.where(df['data_dir'] == '/home/cveenker1/Anomaly-Detection-in-API-calls/data/real_data2').dropna()


print(df_syn)
print(df_rl)

df_syn_vy = df_syn.where(df_syn['Model'] == 'Vaeganomaly').dropna()
# df_rl_vy =  df_rl.where(df_rl['vaegan'] == 0.0).dropna()
# df_syn_v = df_syn.where(df_syn['vaegan'] == 0.0).dropna()
# df_rl_v = df_rl.where(df_rl['vaegan'] == 1.0).dropna()

params = ['epochs','z_dim', 'learning_rate', 'num_filters']
labels = ['Epochs','Z-Dimension','Learning Rate', 'Number of Filters']

dfs = [df_syn,df_rl]
for i, param in enumerate(params):
    # df1 = dfs[i].where(dfs[0][params[(i+1)%4]] ==50).dropna()
    # df1 = df1.where(df1[params[(i+2)%4]] == 0.001).dropna()
    # df1 = df1.where(df1[params[(i+3)%4]] ==20).dropna()
    # print('params',params[(i+1)%4],params[(i+2)%4],params[(i+3)%4])
    ax =sns.lineplot(data=dfs[1], y=param, x="test_accuracy",errorbar='sd',sort=True, err_style='band', style='Model', hue="Model")
    ax.set_xlabel('Test Accuracy',fontsize='large')
    ax.set_ylabel(labels[i],fontsize='large')
    plt.grid()
    plt.savefig('hparam_tune' + param +'.png',bbox_inches="tight", dpi=800)

    plt.show()


import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.tri import Triangulation
from scipy.interpolate import make_interp_spline
from scipy.interpolate import interp1d

X = df_syn_vy['z_dim']
Y = df_syn_vy['num_filters']
Z = df_syn_vy['test_accuracy']
 
print(X,Y,Z)
fig = plt.figure(figsize=(10, 8))
ax = plt.axes(projection='3d')
 
surf = ax.plot_trisurf(X, Y, Z, cmap='cool', alpha=0.8,norm='linear')
ax.set_title('Hyperparameter Tuning', fontsize='large')
fig.colorbar(surf, shrink=0.5, aspect=5)

ax.set_xlabel('Z-Dimension', fontsize='large')
ax.set_ylabel('Number of Filters', fontsize='large')
ax.set_zlabel('Test Accuracy', fontsize='large')
plt.savefig('hparam3d.png',bbox_inches="tight", dpi=800)
plt.show()