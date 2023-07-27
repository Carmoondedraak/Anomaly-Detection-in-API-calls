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



from category_encoders import *
from flows import *
from feature_encodings import *
from preprocessing import *
from visualising_dataset import *

class Feature_Selection():
    '''This object performs feature selection using various machine learning models'''

    def __init__(self,k,data,savefolder):
        '''create the needed encoder object and splitter for train-val-test set, initiate models and filters
            * data - list of two dataframes (normal data and abnormal data)'''
        self.savefolder = savefolder
        encoder_obj = Encoders()
        encoders = encoder_obj.encoders
        filter_obj = Filters()

        splitter = Train_Val_Test_split()
        filters = self.filters()
        model = self.models()
        if not os.path.exists(self.savefolder):
        # If it doesn't exist, create it
            os.makedirs(self.savefolder)
        result_scores = []
        # loop over each model to be used as a classifier
        for classifier in model.items():
            # try every encoding method

            for encoder in encoders:
                print('this enocoder is being used:',encoder)
                X_n = encoder_obj.choose_encoding(data[0],encoder)
                X_a = encoder_obj.choose_encoding(data[1],encoder)
                splitter.split_dataset([X_n,X_a])
                X = splitter.train_set
                data_tabling(X)
                y = splitter.train_targets
                X_test  = splitter.test_set
                y_test = splitter.test_targets

                # see which filter works the best
                for filt in filters.items():
                    print('this filter is being used:',filt)
                    prediction,feature_names, pred_prob = self.pipes_filt(X, y,X_test,y_test, filt, classifier, k)
                    accuracy, precision, recall, auc = self.scores(prediction,y_test, pred_prob,filt[0],classifier[0])
                    result_scores.append([filt[0],classifier[0],feature_names,accuracy,precision, recall])

                    df = pd.DataFrame(result_scores,columns = ['filter/model', 'classifier', 'feature_names','accuracy', 'precision', 'recall'])

                    # save pandas dataframe to pickle and add to existing pickle when new user is spawned
                    file = self.savefolder+'/scores.pkl'
                    if os.path.isfile(file):
                        df_prev =  pd.read_pickle(self.savefolder+'/scores.pkl')
                        df = pd.concat([df,df_prev],ignore_index=True)
                    df.to_pickle(file)
                    
                # see which model works the best using sfs selection 
                for fs in model.items():
                    print(fs, classifier)
                    # make sure the feature selection model and classifier are not the same
                    if classifier != fs:
                        prediction, feature_names, pred_prob = self.pipes_model(X,y,X_test,y_test,fs,classifier,k, 'forward')
                        accuracy, precision, recall, auc = self.scores(prediction,y_test, pred_prob,fs[0],classifier[0])
                        result_scores.append([fs[0],classifier[0],feature_names, accuracy,precision, recall])
                        pd.DataFrame(result_scores,columns = ['filter/model', 'classifier', 'feature_names','accuracy', 'precision', 'recall'])

                        if os.path.isfile(file):
                            df_prev =  pd.read_pickle(self.savefolder+'/scores.pkl')
                            df = pd.concat([df,df_prev],ignore_index=True)
                        df.to_pickle(file)
    def models(self):
        '''initiate the different models '''
        lr = LogisticRegression(max_iter=10000)
        knn = KNeighborsClassifier(n_neighbors=3)
        rf = RandomForestClassifier()
        svc = SVC()
        dt = DecisionTreeClassifier(random_state=0)
        return {"lr": lr, "knn":knn, "rf":rf, 'svc':svc, "dt":dt}
    
    def filters(self):
        '''initiate the different filters'''
        mutual = mutual_info_classif
        fisher = f_classif
        chi = chi2
        return {'mutinf': mutual,'fisher':fisher, 'choi':chi }
        
    def pipes_model(self, X, y,X_test,y_test, model, classifier, k, direction):
        '''pipeline for feature selection using sfs and a classifier'''
        clf = Pipeline([(model[0], SequentialFeatureSelector(model[1],n_features_to_select=k)),
                        (classifier[0], classifier[1])])
        clf.fit(X, y)
        print('training accuracy:',accuracy_score(y, clf.predict(X)))
        prediction = clf.predict(X_test)
        pred_prob = clf.predict_proba(X_test)
        print('the model used and the classifier used:', model[0],classifier[0], prediction)

        print('the best features:',clf[:-1].get_feature_names_out())
        self.visualise(clf,X,y,model[0],classifier[0],np.linspace(0.1,1.0,10),'')
        self.visualise(clf,X,y,model[0],classifier[0], np.arange(1,2181,100),'ext')

        return prediction, clf[:-1].get_feature_names_out(), pred_prob
    
    def pipes_filt(self, X, y,X_test,y_test, filt, classifier, k):
        '''pipeline for feature selection using filter and classifier'''
        clf = Pipeline([(filt[0], SelectKBest(filt[1],k=k)),
                        (classifier[0], classifier[1])])
        clf.fit(X, y)
        print('training accuracy:',accuracy_score(y, clf.predict(X)))

        prediction = clf.predict(X_test)
        pred_prob = clf.predict_proba(X_test)
        print('the filter used and the classifier used:',filt[0],classifier[0], prediction, y_test)
        print('the best features', clf[:-1].get_feature_names_out())

        self.visualise(clf,X,y,filt[0],classifier[0], np.linspace(0.1,1.0,10),'')
        self.visualise(clf,X,y,filt[0],classifier[0], np.arange(1,2181,100),'ext')

        return prediction, clf[:-1].get_feature_names_out(), pred_prob

    def scores(self, y_pred,y_true, pred_prob, model, classifier):
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        # auc = roc_auc_score(y_true,pred_prob)
        auc = 0
        # r = confusion_matrix(y_true, y_pred)
        cm = confusion_matrix(y_true, y_pred, labels=[0,1])
        disp = ConfusionMatrixDisplay(confusion_matrix=cm,display_labels=['normal','abnormal'])
        disp.plot()
        plt.savefig(self.savefolder+'/confusion_matrix_'+model+classifier+".png")


        print('these are the metrics:\n accuracy:',accuracy,'\n precision:',precision,'\n recall',recall,'\n auc',auc)

        return accuracy, precision, recall, auc

    def visualise(self,clf,X,y, filt,classifier, train_sizes, filename):
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
        plt.savefig(self.savefolder + '/' + filt+'_'+classifier+filename+".png")
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
        plt.savefig(self.savefolder + '/'+ filt + '_' + classifier +'fit'+ '.png' )
        plt.clf()

    # def extra(self):
    #     pipe = Pipeline([('selector', SelectKBest(filt, k=5)),
    #              ('classifier', LogisticRegression())])

    #     search_space = [{'selector__k': [5, 10, 20, 30]},
    #             {'classifier': [LogisticRegression(max_iter=1000)],
    #              'classifier__C': [0.01, 0.1, 1.0]},
    #             {'classifier': [RandomForestClassifier(n_estimators=100)],
    #              'classifier__max_depth': [5, 10, None]},
    #             {'classifier': [KNeighborsClassifier()],
    #              'classifier__n_neighbors': [3, 7, 11],
    #              'classifier__weights': ['uniform', 'distance']},
    #             {'classifier':[SVC()],
    #              'classifier__kernel': ['linear', 'poly']},
    #             {'classifier': [DecisionTreeClassifier(random_state=0)],
    #              'classifier__criterion': ['entropy', 'log_loss']}]
            

if __name__=="__main__":
    # the parser
    parser = argparse.ArgumentParser(
                    prog='Feature Selection',
                    description='This program performs feature selection using various different machine learning methods',
                    epilog='Text at the bottom of help')

    parser.add_argument('filename',metavar= 'filename of normal dataset')           # positional argument
    parser.add_argument('filename1',metavar= 'filename of abnormal dataset')
    parser.add_argument('savefile', metavar= 'the file to save the prerocessed dataset')
    args = parser.parse_args()

    # load the preprocessed dataset
    data_n = pd.read_pickle(args.filename)
    data_a = pd.read_pickle(args.filename1)
    
    # categorical and numerical data defined
    categorical_feats = ['user_agent','response_line','cache_control', 'content_length','server','file_data','dst','src','src_p','dst_p','request_method','request_uri','request_uri_query','x_forwarded_for','user_agent','cookie','transfer_encoding','referer','authorization','authbasic','content_type','response_code']
    numerical = ['time']

    # create data preprocessing object
    data_preprocessor = Data_Preprocess(data_n,data_a)

    # change the values to string and float formats
    data_n = data_preprocessor.change_values(data_n,numerical,categorical_feats)
    data_a = data_preprocessor.change_values(data_a,numerical,categorical_feats)
    data = [data_n,data_a]

    # start feature selection 
    FS = Feature_Selection(2, data, args.savefile)
