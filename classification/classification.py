from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn import metrics
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.ensemble import AdaBoostClassifier
import numpy as np
from sklearn.pipeline import Pipeline
import pandas as pd
import pickle
pd.options.mode.chained_assignment = None 


def testing_model(data, cviteration, size,column_use,target):
    train = data.iloc[0:int(size),:]
    test = data.iloc[int(size):,:]
    count = 0
    accuracy = 0
    for _ in range(cviteration):
        xtest = data.iloc[((data.shape[0]-size)*count):((data.shape[0]-size)*(count+1)),:]
        train1 = data.iloc[((data.shape[0]-size)*(count+1)):,:]
        train2 = data.iloc[0:((data.shape[0]-size)*count),:]
        xtrain = pd.concat([train1,train2])
        xresult =0
        prediction = pd.DataFrame()
        #~73%
        predicted_svm_rf_nb = ensemble_voting_classification(xtrain,xtest,column_use,target)
        prediction = pd.Series(predicted_svm_rf_nb, index=xtest.index)
        
        #~73%
        #predicted_svm = svm_classification(xtrain,xtest,column_use,target)
        #prediction = pd.Series(predicted_svm, index=xtest.index)
        
        #~65%
        #predicted_rf = rf_classification(xtrain,xtest,column_use,target)
        #prediction = pd.Series(predicted_rf, index=xtest.index)
        
        #accuracy ~60%
        #predicted_knn = knn_classification(xtrain,xtest,column_use,target)
        #prediction= pd.Series(predicted_knn, index=xtest.index)
        
        #accuracy ~56%
        #predicted_nb = nb_classification(xtrain,xtest,column_use,target)
        #prediction = pd.Series(predicted_nb, index=xtest.index)
        
        #accuracy ~60%, slow
        #predicted_mlp = mlp_classification(xtrain,xtest,column_use,target)
        #prediction = pd.Series(predicted_mlp, index=xtest.index)
        
        xresult = xresult+np.mean(prediction == xtest[target])
        #xresult = xresult+np.mean("NEGATIVE" == xtest[target])
        
        #print(metrics.classification_report(xtest[target], prediction["prediction1"],["POSITIVE","NEUTRAL","NEGATIVE"]))
        
        count = count+1
        accuracy=accuracy+xresult
    #print("SGDClassifier (5 iteration cv)")
    print("accuracy:")
    print(accuracy/cviteration)
    
def ensemble_voting_classification(train, test,column_use,target):
    pipe_svm  = Pipeline([('vect', CountVectorizer(ngram_range=(1, 1),token_pattern=r'\b\w+\b', min_df=1)),
                      ('tfidf', TfidfTransformer()),
                      ('clf-svm', SGDClassifier(loss='hinge', penalty='l2',alpha=1e-3, n_iter=10, random_state=42)),
    ])
    pipe_rf  = Pipeline([('vect', CountVectorizer(ngram_range=(1,1),token_pattern=r'\b\w+\b', min_df=2)),
                      ('tfidf', TfidfTransformer()),
                      ('clf-rf', RandomForestClassifier(random_state=1)),
    ])
    pipe_nb  = Pipeline([('vect', CountVectorizer(ngram_range=(1, 1),token_pattern=r'\b\w+\b', min_df=1)),
                      ('tfidf', TfidfTransformer()),
                      ('clf', MultinomialNB()),
    ])
    pipe = Pipeline([['clf3', VotingClassifier(estimators=[("clf-svm",pipe_svm), ("clf-rf",pipe_rf), ("clf-nb",pipe_nb)], weights=[2,1,1])]])
    text_clf = pipe.fit(train[column_use], train[target])
    predicted = text_clf.predict(test[column_use])
    return predicted

def nb_classification(train, test,column_use,target ):
    pipe = Pipeline([('vect', CountVectorizer(ngram_range=(1, 1),token_pattern=r'\b\w+\b', min_df=1)),
                      ('tfidf', TfidfTransformer()),
                      ('clf', MultinomialNB()),
    ])
    text_clf = pipe.fit(train[column_use], train[target])

    predicted = text_clf.predict(test[column_use])
    return predicted

def rf_classification(train, test,column_use,target ):
    pipe  = Pipeline([('vect', CountVectorizer(ngram_range=(1, 1),token_pattern=r'\b\w+\b', min_df=1)),
                      ('tfidf', TfidfTransformer()),
                      ('clf-rf', RandomForestClassifier(n_estimators =50,random_state=1,criterion="entropy")),
    ])
    text_clf_rf  = pipe .fit(train[column_use], train[target])
    predicted_rf = text_clf_rf.predict(test[column_use])
    return predicted_rf

def svm_classification(train, test,column_use,target ):
    pipe  = Pipeline([('vect', CountVectorizer(ngram_range=(1, 1),token_pattern=r'\b\w+\b', min_df=1)),
                      ('tfidf', TfidfTransformer()),
                      ('clf-svm', SGDClassifier(loss='hinge', penalty='l2',alpha=1e-3, n_iter=10, random_state=42)),
    ])
    text_clf_svm  = pipe .fit(train[column_use], train[target])
    predicted_svm = text_clf_svm.predict(test[column_use])
    return predicted_svm

def knn_classification(train, test,column_use,target ):
    pipe  = Pipeline([('vect', CountVectorizer(ngram_range=(1, 1),token_pattern=r'\b\w+\b', min_df=1)),
                      ('tfidf', TfidfTransformer()),
                      ('clf-knn', KNeighborsClassifier(n_neighbors=10, weights='uniform', 
                                                       algorithm='auto', leaf_size=30, p=2, metric='minkowski', 
                                                       metric_params=None, n_jobs=1)),
    ])
    text_clf_knn  = pipe .fit(train[column_use], train[target])
    predicted_knn = text_clf_knn.predict(test[column_use])
    return predicted_knn

def mlp_classification(train, test,column_use,target ):
    pipe  = Pipeline([('vect', CountVectorizer(ngram_range=(1, 1),token_pattern=r'\b\w+\b', min_df=1)),
                      ('tfidf', TfidfTransformer()),
                      ('clf-mlp', MLPClassifier(activation='relu', alpha=1e-05, batch_size='auto',
       beta_1=0.9, beta_2=0.999, early_stopping=False,
       epsilon=1e-08, hidden_layer_sizes=(30, 2), learning_rate='constant',
       learning_rate_init=0.001, max_iter=200, momentum=0.9,
       nesterovs_momentum=True, power_t=0.5, random_state=1, shuffle=True,
       solver='lbfgs', tol=0.0001, validation_fraction=0.1, verbose=False,
       warm_start=False)),
    ])
    text_clf_mlp  = pipe.fit(train[column_use], train[target])
    predicted_mlp = text_clf_mlp.predict(test[column_use])

    #test["predicted_mlp"]=pd.Series(predicted_mlp, index=test.index)
    return predicted_mlp

def build_model(data,column_use,target):
    #prepare train and test data 
    
    #train_size = int((len(data)/6)*5)
    train_size = int((len(data)/1000)*999)
    test_size = len(data)-train_size
    train = data.iloc[0:train_size,:]
    test = data.iloc[train_size:,:]
    train.to_csv("train_data.csv",  encoding="utf-8")
    
    #prepare model builder
    pipe_svm  = Pipeline([('vect', CountVectorizer(ngram_range=(1, 1),token_pattern=r'\b\w+\b', min_df=1)),
                      ('tfidf', TfidfTransformer()),
                      ('clf-svm', SGDClassifier(loss='hinge', penalty='l2',alpha=1e-3, n_iter=10, random_state=42)),
    ])
    pipe_rf  = Pipeline([('vect', CountVectorizer(ngram_range=(1,1),token_pattern=r'\b\w+\b', min_df=2)),
                      ('tfidf', TfidfTransformer()),
                      ('clf-rf', RandomForestClassifier(random_state=1)),
    ])
    pipe_nb  = Pipeline([('vect', CountVectorizer(ngram_range=(1, 1),token_pattern=r'\b\w+\b', min_df=1)),
                      ('tfidf', TfidfTransformer()),
                      ('clf', MultinomialNB()),
    ])
    pipe = Pipeline([['clf3', VotingClassifier(estimators=[("clf-svm",pipe_svm), ("clf-rf",pipe_rf), ("clf-nb",pipe_nb)], weights=[2,1,1])]])
    
    #build model
    model = pipe.fit(train[column_use], train[target])

    #predict the test data
    predicted = model.predict(test[column_use])
    
    #evaluation
    print("metrics:")
    print(metrics.classification_report(test[target], predicted,["POSITIVE","NEUTRAL","NEGATIVE"]))
    print("accuracy:")
    print(np.mean(predicted == test[target]))
    test["predict"]=pd.Series(predicted, index=test.index)
    test.to_csv("test_data.csv",  encoding="utf-8")
    
    #return model
    return model
    
    
data = pd.read_csv('review2.csv',sep=',')
#print columns
print(data.columns.values.tolist())
#using 1/6 for testing in Cross validation 
cviteration = 6
#size of train data
size = int((data.shape[0]/cviteration)*(cviteration-1)) 
#randomize the rows
data = data.sample(frac=1)
#specified columns used
column_use = "lemmatizing"
target = "label"
#validating modal
testing_model(data, cviteration, size,column_use,target)

#build model 
model = build_model(data,column_use,target)

#save model
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)                       

    