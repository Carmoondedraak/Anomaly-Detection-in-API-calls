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
from sklearn.metrics import accuracy_score, precision_score

from category_encoders import *
from flows import *
from feature_encodings import *
from preprocessing import *

class Feature_Selection():
    '''This object performs feature selection using various machine learning models'''

    def __init__(self,k,data):
        '''create the needed encoder object and splitter for train-val-test set, initiate models and filters
            * data - list of two dataframes (normal data and abnormal data)'''
        encoder_obj = Encoders()
        encoders = encoder_obj.encoders
        filter_obj = Filters()
        splitter = Train_Val_Test_split()
        filters = self.filters()
        model = self.models()
        
        accuracy = {}
        precision = {}
        recall = {}
        auc = {}
        # loop over each model to be used as a classifier
        for classifier in model.items():
            # try every encoding method
            for encoder in encoders:
                print('this enocoder is being used:',encoder)
                X_n = encoder_obj.choose_encoding(data[0],encoder)
                X_a = encoder_obj.choose_encoding(data[1],encoder)
                splitter.split_dataset([X_n,X_a])
                X = splitter.train_set
                y = splitter.train_targets
                X_test  = splitter.test_set
                y_test = splitter.test_targets

                # see which filter works the best
                for filt in filters.items():
                    print('this filter is being used:',filt)
                    # feats = filter_obj.choose_filter(filt, X, y, k)
                    # print('these features are being used:', feats)
                    prediction,feature_names, pred_prob = self.pipes_filt(X, y,X_test,y_test, filt, classifier, k)
                    accuracy, precision, recall, auc = self.scores(prediction,y_test, pred_prob)
                # see which model works the best using sfs selection 
                for fs in model.items():
                    print(fs, classifier)
                    # make sure the feature selection model and classifier are not the same
                    if classifier != fs:
                        prediction, feature_names, pred_prob = self.pipes_model(X,y,X_test,y_test,fs,classifier,5, 'forward')
                        accuracy, precision, recall, auc = self.scores(prediction,y_test, pred_prob)
                        accuracy[(fs,classifier)] = accuracy
                        precision[(fs,classifier)] = precision
                        recall[(fs,classifier)] = recall
                        auc[(fs,classifier)] = auc
    def models(self):
        '''initiate the different models '''
        lr = LogisticRegression(max_iter=1000)
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
        clf = Pipeline([(model[0], SequentialFeatureSelector(model[1],n_features_to_select=5)),
                        (classifier[0], classifier[1])])
        clf.fit(X, y)
        prediction = clf.predict(X_test)
        pred_prob = clf.predict_proba(X)
        print('the model used and the classifier used:', model[0],classifier[0], prediction)
        print('the best features:',clf[:-1].get_feature_names_out())
        return prediction, clf.get_feature_names_out(), pred_prob
    
    def pipes_filt(self, X, y,X_test,y_test, filt, classifier, k):
        '''pipeline for feature selection using filter and classifier'''
        clf = Pipeline([(filt[0], SelectKBest(filt[1],k=k)),
                        (classifier[0], classifier[1])])
        clf.fit(X, y)
        prediction = clf.predict(X_test)
        pred_prob = clf.predict_proba(X)
        print('the filter used and the classifier used:',filt[0],classifier[0], prediction, y_test)
        print('the best features', clf[:-1].get_feature_names_out())
        return prediction, clf[:-1].get_feature_names_out(), pred_prob

    def scores(self, y_pred,y_true, pred_prob):
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        auc = roc_auc_score(y_true,pred_prob)
        print('these are the metrics:\n accuracy:',accuracy,'\n precision:',precision,'\n recall',recall,'\n auc',auc)

        return accuracy, precision, recall, auc

    def visualise(self,):
        pass

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
    #              'classifier__weights': ['uniform', 'distance']}]
    #             {'classifier':[SVC()],'classifier__'}]
            
        # dt = DecisionTreeClassifier(random_state=0)   

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
    FS = Feature_Selection(5, data)
