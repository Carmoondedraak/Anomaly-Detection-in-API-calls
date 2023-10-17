from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from skfeature.function.similarity_based import fisher_score
from sklearn.feature_selection import mutual_info_classif
from sklearn.feature_selection import SequentialFeatureSelector
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import f_classif
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import LearningCurveDisplay, learning_curve
import matplotlib.pyplot as plt
import os
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import GridSearchCV
from joblib import dump, load

from category_encoders import *
from flows import *
from feature_encodings import *
from preprocessing import *
from visualising_dataset import *

class Feature_Selection():
    '''This object performs feature selection using various machine learning models'''

    def __init__(self,k,data,savefolder, perc):
        '''create the needed encoder object and splitter for train-val-test set, initiate models and filters
            * data - list of two dataframes (normal data and abnormal data)'''
        self.savefolder = savefolder
        self.perc = perc
        encoder_obj = Encoders()
        encoders = encoder_obj.encoders
        filter_obj = Filters()

        self.splitter = Train_Val_Test_split()
        filters = self.filters()
        model = self.models()
        
        if not os.path.exists(self.savefolder):
        # If it doesn't exist, create it
            os.makedirs(self.savefolder)
        
        # loop over each model to be used as a classifier
        for classifier in model.items():
            self.classifier = classifier
            # try every encoding method
            for encoder in encoders:
                self.encoder = encoder
                print('this enocoder is being used:',encoder)
                X_n = encoder_obj.choose_encoding(data[0],encoder)
                X_a = encoder_obj.choose_encoding(data[1],encoder)
                self.splitter.split_dataset([X_n,X_a])
                X = pd.concat((self.splitter.train_set,self.splitter.val_set))
                data_tabling(X)
                y = pd.concat((self.splitter.train_targets,self.splitter.val_targets))
                X_test  = self.splitter.test_set
                y_test = self.splitter.test_targets

                # see which filter works the best
                for filt in filters.items():
                    self.model = filt
                    print('this filter is being used:',filt)
                    self.flag = 'selector'
                    search_space = self.hyperparameters()
                    pipe = self.pipe()
                    prediction,feature_names, pred_prob, predictions = self.pipes_train(X, y,X_test,y_test, search_space, pipe)
                    accuracy, precision, recall, auc = self.scores(prediction,y_test, pred_prob, 0.5, test=False)
                    res = [filt[0],classifier[0],self.encoder ,feature_names,accuracy,precision, recall] + [x for x in predictions]
                    self.save_results(res)
                    
                # see which model works the best using sfs selection 
                for fs in model.items():
                    self.model = fs
                    print(fs, classifier)
                    # make sure the feature selection model and classifier are not the same
                    if classifier != fs:
                        self.flag = 'fs'
                        search_space = self.hyperparameters()
                        pipe = self.pipe()
                        prediction, feature_names, pred_prob,predictions = self.pipes_train(X,y,X_test,y_test, search_space,pipe)
                        accuracy, precision, recall, auc = self.scores(prediction,y_test, pred_prob, 0.5, test=False)
                        res = [fs[0],classifier[0],self.encoder,feature_names, accuracy,precision, recall]+[x for x in predictions]
                        self.save_results(res)
    
    def models(self):
        '''initiate the different models '''
        lr = LogisticRegression(max_iter=10000)
        knn = KNeighborsClassifier(n_neighbors=3)
        rf = RandomForestClassifier()
        svc = SVC()
        dt = DecisionTreeClassifier(random_state=0)
        return {"lr": lr, "knn":knn, "rf":rf, 'svc':svc, "dt":dt}

    def hyperparameters(self):
        '''Initiate the hyperparameters for hyperparameter tuning'''
        if self.flag == 'fs':
            selector = 'selector__n_features_to_select'
        elif self.flag == 'selector':
            selector = 'selector__k'

        search_space_lr = {selector: [2, 5, 10, 15],
            'classifier__C': [0.01, 0.1, 1.0]}
        search_space_rf = {selector: [2, 5, 10, 15],
            'classifier__max_depth': [5, 10, None]}
        search_space_knn = {selector: [2, 5, 10, 15],
            'classifier__n_neighbors': [3, 7, 11],
            'classifier__weights': ['uniform', 'distance']}
        search_space_svc = {selector: [2, 5, 10, 15],
            'classifier__kernel': ['linear', 'poly']}
        search_space_dt = {selector: [2, 5, 10, 15],        
            'classifier__criterion': ['entropy', 'log_loss']}
        
        search_space = {'lr':search_space_lr,'rf':search_space_rf,'knn':search_space_knn,'svc': search_space_svc, 'dt':search_space_dt}
        return search_space[self.classifier[0]]
    
    def filters(self):
        '''initiate the different filters'''
        mutual = mutual_info_classif
        fisher = f_classif
        chi = chi2
        return {'mutinf': mutual,'fisher':fisher, 'choi':chi }
        
    def pipe(self):
        '''creating the different pipelines'''
        if self.flag == 'selector':
            clf = Pipeline([('selector', SelectKBest(self.model[1])),
                    ('classifier', self.classifier[1])])
        elif self.flag == 'fs':
            clf = Pipeline([('selector', SequentialFeatureSelector(self.model[1])),
                    ('classifier', self.classifier[1])])
        print('the filter used and the classifier used:',self.model[0],self.classifier[0])
        return clf
    
    def pipes_train(self, X, y,X_test,y_test, search_space,clf):
        '''pipeline for feature selection using filter and classifier'''

        search = GridSearchCV(clf, search_space,cv=5, scoring='accuracy', n_jobs=5)
        search.fit(X,y)
        print('training accuracy:',accuracy_score(y, search.predict(X)))

        prediction = search.predict(X_test)
        pred_prob = search.predict_proba(X_test)
       
        print('the best features',search.best_estimator_)
        print(X.columns[search.best_estimator_.named_steps['selector'].get_support()])

        results = search.cv_results_
        pd.DataFrame.from_dict(results).to_pickle(self.savefolder +'/'+self.model[0]+'_'+self.classifier[0]+'_tuneresults'+'.pkl')
        predictions = self.pipe_test(search)
        self.visualise(search,X,y, np.linspace(0.1,1.0,10),'')
        self.visualise(search,X,y, np.arange(1,2181,100),'ext')

        self.save_model(search)
        return prediction, X.columns[search.best_estimator_.named_steps['selector'].get_support()], pred_prob, predictions

    def pipe_test(self,pipe):
        results = []
        for i in range(len(self.perc)):
            test_a = self.splitter.test_a.sample(frac=self.perc[i])
            test_n = self.splitter.test_n
            test_X = pd.concat([test_n,test_a], ignore_index=True)
            test_targets = test_X['target']
            test_X = test_X.drop(['target'],axis=1)

            prediction = pipe.predict(test_X)
            pred_prob = pipe.predict_proba(test_X)
            # prediction = pipe.score(test_X,test_targets)
            scoress = self.scores(prediction, test_targets, pred_prob, self.perc[i])
            results.append(scoress)
        return results

    def scores(self, y_pred,y_true, pred_prob, B,test=True):
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)

        auc = roc_auc_score(y_true,pred_prob)
        # auc = 0
        cm = confusion_matrix(y_true, y_pred, labels=[0,1])
        tn = cm[0][0]
        fn = cm[1][0]
        tp = cm[1][1]
        fp = cm[0][1]
        ppv = (tp * B) / (tp *B + fp *(1-B))
        print('ppv',ppv)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm,display_labels=['normal','abnormal'])
        disp.plot()
        plt.savefig(self.savefolder+'/confusion_matrix_'+self.model[0]+self.classifier[0]+".png")

        print('these are the metrics:\n accuracy:',accuracy,'\n precision:',precision,'\n recall',recall,'\n auc',auc)
        if test == False: 
            return {'accuracy':accuracy, 'precision':precision, 'recall':recall, 'auc':auc, 'ppv':ppv}
        return {'accuracy_{}'.format(B):accuracy, 'precision_{}'.format(B):precision, 'recall_{}'.format(B):recall, 'auc_{}'.format(B):auc, 'ppv_{}'.format(B):ppv}

    def visualise(self,clf,X,y,train_sizes, filename):
        train_sizes, train_scores, test_scores, fit_times, score_times = learning_curve(estimator=clf, X=X, y=y,
                                                       cv=10, train_sizes=train_sizes,
                                                     n_jobs=1, return_times=True)

        train_scores = np.nan_to_num(train_scores)
        test_scores =np.nan_to_num(test_scores)

        train_mean = np.mean(train_scores, axis=1)
        train_std =  np.std(train_scores, axis=1)
        test_mean = np.mean(test_scores, axis=1)
        test_std = np.std(test_scores, axis=1)

        # Create the plot using Matplotlib
        plt.figure()
        plt.plot(train_sizes, train_mean, color='blue', marker='o', markersize=5, label='Training Accuracy')
        plt.fill_between(train_sizes, train_mean + train_std, train_mean - train_std, alpha=0.15, color='blue')
        plt.plot(train_sizes, test_mean, color='green', marker='+', markersize=5, linestyle='--', label='Validation Accuracy')
        plt.fill_between(train_sizes, test_mean + test_std, test_mean - test_std, alpha=0.15, color='green')
        plt.title('Learning Curve')
        plt.xlabel('Training Data Size')
        plt.ylabel('Model accuracy')
        plt.grid()
        plt.legend(loc='lower right')
        plt.savefig(self.savefolder + '/' + self.model[0]+'_'+self.classifier[0]+filename+".png")
        plt.clf()

        fig, ax = plt.subplots(nrows=2, figsize=(16, 12), sharex=True)

        fit_mean = np.mean(fit_times,axis=1)
        fit_std = np.std(fit_times,axis=1)
        score_mean = np.mean(score_times,axis=1)
        score_std = np.std(score_times,axis=1)

        ax[0].plot(train_sizes, fit_mean, "o-")
        ax[0].fill_between(
            train_sizes,
            fit_mean - fit_std,
            fit_mean + fit_std,
            alpha=0.3,
        )
        ax[0].set_ylabel("Fit time (s)")
        ax[0].set_title(
            f"Scalability of the {clf.__class__.__name__} classifier"
        )

        # scalability regarding the score time
        ax[1].plot(train_sizes, score_mean, "o-")
        ax[1].fill_between(
            train_sizes,
            score_mean - score_std,
            score_mean + score_std,
            alpha=0.3,
        )
        ax[1].set_ylabel("Score time (s)")
        ax[1].set_xlabel("Number of training samples")
        plt.savefig(self.savefolder + '/'+ self.model[0] + '_' + self.classifier[0] +'fit'+ '.png' )
        plt.clf()

    def save_results(self,result_scores):
        df = pd.DataFrame(result_scores, columns = ['filter/model', 'classifier','encoder', 'feature_names','accuracy', 'precision', 'recall']+ ['test_acc_perc_'+i for i in self.perc] +  ['test_precision_perc_'+i for i in self.perc] +  ['test_recall_perc_'+i for i in self.perc] +  ['test_auc_perc_'+i for i in self.perc]+ ['test_ppv_perc_'+i for i in self.perc]) 

        # save pandas dataframe to pickle and add to existing pickle when new user is spawned
        file = self.savefolder+'/scores.pkl'
        if os.path.isfile(file):
            df_prev =  pd.read_pickle(self.savefolder+'/scores.pkl')
            df = pd.concat([df,df_prev],ignore_index=True)
        df.to_pickle(file)

    def save_model(self,model):
        '''saves the model to a joblib file'''
        dump(model, self.savefolder+'/model_weights_'+self.model[0]+'_'+ self.classifier[0]+'.joblib') 

    def load_models(self, filename):
        '''loads the model from a joblib file'''
        clf = load(self.savefolder +'/'+ filename)
        return clf

if __name__=="__main__":
    # the parser
    parser = argparse.ArgumentParser(
                    prog='Feature Selection',
                    description='This program performs feature selection using various different machine learning methods',
                    epilog='Text at the bottom of help')

    parser.add_argument('filename',metavar= 'filename of normal dataset')           # positional argument
    parser.add_argument('filename1',metavar= 'filename of abnormal dataset')
    parser.add_argument('savefile', metavar= 'the file to save the prerocessed dataset')
    parser.add_argument('--perc', metavar='anomaly percentages that should be used during testing', default=[0.5,0.2,0.01,0.001,0.0001])
    args = parser.parse_args()
    print(args.perc)
    # load the preprocessed dataset
    data_n = pd.read_pickle(args.filename)
    data_a = pd.read_pickle(args.filename1)
    
    # categorical and numerical data defined
    categorical_feats = ['user_agent','response_line','cache_control', 'content_length','server','file_data','dst','src','src_p','dst_p','request_method','request_uri','request_uri_query','x_forwarded_for','user_agent','cookie','transfer_encoding','referer','authorization','authbasic','content_type','response_code']
    numerical = ['time']

    # create data preprocessing object
    data_preprocessor = Data_Preprocess([data_n,data_a])

    # change the values to string and float formats
    data_n = data_preprocessor.change_values(data_n,numerical,categorical_feats)
    data_a = data_preprocessor.change_values(data_a,numerical,categorical_feats)
    data = [data_n,data_a]

    # start feature selection 
    FS = Feature_Selection(2, data, args.savefile, args.perc)
