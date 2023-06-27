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

from category_encoders import *
from flows import *
from feature_encodings import *
from preprocessing import *

class Feature_Selection():
    def __init__(self, X,y, test_X,test_y ,k):
        encoder_obj = Encoders()
        encoders = encoder_obj.encoders
        filters = self.filters()
        model = self.models()
        
        for classifier in model.items():
            for encoder in encoders:
                print(encoder)
                X = encoder_obj.choose_encoding(X,encoder)
                test_X = encoder_obj.choose_encoding(test_X,encoder)
                for filt in filters.items():
                    print(filt)
                    feats = filter_obj.choose_filter(filt, X, y, k)
                    print(feats)
                    self.pipes_filt(X, y,X_test,y_test, filt, classifier, k, direction)
                    
                for fs in model.items():
                    print(fs, classifier)
                    if classifier != fs:
                        self.pipes_model(X,y,test_X,test_y,fs,classifier,5, 'forward')
       
        
    def models(self):
        lr = LogisticRegression(max_iter=1000)
        knn = KNeighborsClassifier(n_neighbors=3)
        rf = RandomForestClassifier()
        svc = SVC()
        dt = DecisionTreeClassifier(random_state=0)
        return {"lr": lr, "knn":knn, "rf":rf, 'svc':svc, "dt":dt}
    
    def filters():
        mutual = mutual_info_classif()
        fisher = f_classif()
        chi = chi2()
        return {'mutual': mutual,'fisher':fisher, 'chi':chi }
        
    def pipes_model(self, X, y,X_test,y_test, model, classifier, k, direction):
        clf = Pipeline([(model[0], SequentialFeatureSelector(model[1],n_features_to_select=5)),
                        (classify[0], classify[1])])
        clf.fit(X, y)
        score = clf.score(X_test,y_test)
        print(model[0], score)
        print(clf.get_feature_names_out())
        return score, clf.get_feature_names_out()
    
    def pipes_filt(self, X, y,X_test,y_test, filt, classifier, k, direction):
        clf = Pipeline([(filt[0], SelectKbest(filt[1],n_features_to_select=5)),
                        (classify[0], classify[1])])
        clf.fit(X, y)
        score = clf.score(X_test,y_test)
        print(filt[0], score)
        return score, clf.get_feature_names_out()


if __name__=="__main__":

    targets = data['targets']
    categorical_feats = ['user_agent','response_line','cache_control', 'content_length','server','file_data','dst','src','src_p','dst_p','request_method','request_uri','request_uri_query','x_forwarded_for','user_agent','cookie','transfer_encoding','referer','authorization','authbasic','content_type','response_code','date']
    numerical = ['time']
    data_b = data_preprocessor.change_values(train,numerical,categorical_feats)
    display(train)
    FS = Feature_Selection(train, targets, test,test_target, 5)
