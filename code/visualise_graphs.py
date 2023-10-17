import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
def create_graph(data,filename, x_label, y_label):
    # for i in range(len(data)):
    print(data)
    sns.lineplot(data=data, x='Step', y="Value", hue="file", style="set",palette='pastel',errorbar='sd')
    plt.show()


# accuracy train/ val 
# loss train / val 
# loss 2 train /val 

def create_df(files):
    df = pd.DataFrame() 
    names = ['accuracy','discriminator loss', 'generator loss']
    n = ['train','val']
    for i,file in enumerate(files):
        for j,part in enumerate(n):
            print(file)
            f = pd.read_csv(file[j])
            if i == 2:
                i =0
            f['file'] = i
            f['set'] = part
            df = pd.concat((df,f))
    return df

def vis(files):
    files = [['~/Downloads/run-lightning_logs_version_4177468-tag-train_accuracy.csv','~/Downloads/run-lightning_logs_version_4177468-tag-validation_accuracy.csv'], ['~/Downloads/run-lightning_logs_version_4177468-tag-train_discriminator_loss.csv', '~/Downloads/run-lightning_logs_version_4177468-tag-validation_discriminator_loss.csv'],['~/Downloads/run-lightning_logs_version_4180571-tag-train_accuracy_epoch.csv','~/Downloads/run-lightning_logs_version_4180571-tag-validation_accuracy_epoch.csv']]
#  ['~/Downloads/run-lightning_logs_version_4177468-tag-train_total_loss.csv','~/Downloads/run-lightning_logs_version_4177468-tag-validation_total_loss.csv']
    df = create_df(files)
    create_graph(df, 'accuracyandlossgraph.png', 'steps','metrics' )


filename = '~/Documents/Anomaly-Detection-in-API-calls/Results_snellius/Results1/'
df1 = pd.read_pickle(filename + 'scores.pkl')
print(df1)
df2 = pd.read_pickle(filename + 'choi_lr_tuneresults.pkl')
print(df2)
