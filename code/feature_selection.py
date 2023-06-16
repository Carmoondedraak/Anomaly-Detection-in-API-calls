from kmodes.kprototypes import KPrototypes
from kmodes.kmodes import KModes
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn.feature_selection import RFE
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.feature_selection import SequentialFeatureSelector

class Feature_selectors():
    def __init__():

    def measure_predictor_value_woe(woe_df):
        strong_predictors = []
        weak_predictors = []
        medium_predictors = []
        suspicious = []
        useless = []
        very_suspicious = []
        for i, num in enumerate(woe_df['total_IV']):


            if num < 0.5 and num > 0.3:
                strong_predictors.append(woe_df.index[i])
            elif num < 0.1 and num > 0.02:
                weak_predictors.append(woe_df.index[i])
            elif num < 0.02:    
                useless.append(woe_df.index[i])
            elif num > 0.1 and num < 0.3:    
                medium_predictors.append(woe_df.index[i])
            elif num > 0.5 and num < 1:    
                suspicious.append(woe_df.index[i])
            elif num > 1:
                very_suspicious.append(woe_df.index[i])

        print('strong predictors', strong_predictors)
        print()
        print('medium predictors', medium_predictors)
        print()
        print('weak_predcitors', weak_predictors)
        print()
        print('useless', useless)
        print()
        print('suspicious', suspicious)
        print('very suspicious', very_suspicious)

    def clustering(data_m, data):
        
        # k-prototypes
        # k-means with one-hot encoding
        # normalise continuous data (numerical), so that one continuous data is not seen as more important than another. But only one continuous data so for now it does not have to\
        
        kmode = KModes(n_clusters=2, init = "random", verbose=1)
        clusters = kmode.fit_predict(data_m)
        #join data with labels 
        labels = pd.DataFrame(clusters)
        
        data['Cluster_Labels'] = kmode.labels_
        data['Segment'] = data['Cluster_Labels'].map({0:'First', 1:'Second'})
        # Order the cluster
        data['Segment'] = data['Segment'].astype('category')
        data['Segment'] = data['Segment'].cat.reorder_categories(['First', 'Second'])

        
        data['Constant'] = 0 #dummy feature for plotting

        f, axes = plt.subplots(1, 4, figsize=(25, 7), sharex=False)
        f.subplots_adjust(hspace=0.2, wspace=0.7)
        for i in range(4):
            col = data.columns[i]
    #         if i < 2:    
            sns.swarmplot(x=data[col], y=data['Cluster_Labels'], hue=data['Cluster_Labels'], data=data,ax=axes[i])
    #         else:
    #         ax = sns.swarmplot(x=data['Constant'],y=data[col].values,hue=data['Cluster_Labels'],ax=axes[i])
    #         ax.set_title(col)
        plt.close(2)
        plt.close(3)
        plt.show()
        
    def logistic_regression(df):
        y = df['target']
        X = df.drop('target', axis=1)
        model = LogisticRegression()

        # Use RFE to select the top 10 features
    #     rfe = RFE(model, n_features_to_select=10)
    #     rfe.fit(X, y)

    #     # Print the selected features
    #     print(rfe.support_)
        sfs = SequentialFeatureSelector(model, scoring='accuracy',direction='forward')
        sfs.fit(X, y)
    # Use SelectKBest to select the top 10 features
        selector = SelectKBest(chi2, k=10)
        X_new = selector.fit_transform(X, y)

        # Print the selected features
        print(selector.get_support())

        # Print the selected features
        print(sfs.support_)
        # Standardize the train and test sample
    #     scaler = StandardScaler()
    #     X_std = scaler.fit_transform(X)
        
    #     # Perform GridSearchCV to tune best-fit LR model
    #     param = {'C': [10**-2,10**-1,10**0,10**1,10**2]}

    #     lr_model = LogisticRegression(penalty='l1', solver='liblinear')
    #     gs_model = GridSearchCV(estimator=lr_model, param_grid=param)
    #     gs_model.fit(X_std, y)

    #     # Train a LR model with best parameters
    #     model = LogisticRegression(**gs_model.best_params_, penalty='l1', solver='liblinear')
    #     model.fit(X_std, y)
        
    #     coef = model.coef_[0]
    #     imp_features = pd.Series(X.columns)[list(coef!=0)]
    #     X_train = X[imp_features]
    #     print("Redundant Feature Count:",sum(model.coef_[0]==0))
    #     print("Redundant Feature Names:", list(pd.Series(X_train.columns)[list(coef==0)]))

    def SVM():
        pass

    def MCM():
        pass

    def PCA():
        pass
    
    # print(data)

if __name__=="__main__":
