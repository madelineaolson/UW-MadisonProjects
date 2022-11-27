# project: p7
# submitter: maolson8
# partner: none
# hours: 4


import csv
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression, LogisticRegression
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.compose import make_column_transformer
from sklearn.preprocessing import PolynomialFeatures, OneHotEncoder, StandardScaler
    
    
class UserPredictor:
    def __init__(self):
        pass
    def fit(self, train_users, train_logs, train_y):
        # make a dictionary to add new column about time spent on webpage
        time = {}
        for row in train_logs.itertuples():
            try:
                time[row.user_id] += row.seconds
            except:
                time[row.user_id] = row.seconds
        
        # add time column to train_users DataFrame
        time_df = pd.DataFrame.from_dict(time, orient='index')
        train_users = train_users.set_index('user_id').join(time_df).reset_index()
        train_users = train_users.rename(columns={0: "time"})
        train_users = train_users.fillna(0)
        
        # fit with multiple methods and assign to t
        m4 = Pipeline([
            ('poly', PolynomialFeatures()),
            ('scaler', StandardScaler()),
            ('log', LogisticRegression()) ])
        
        model = LogisticRegression(fit_intercept=False)
        
        # make column for each badge to add more features
        oh = OneHotEncoder()
        badges = oh.fit_transform(train_users[['badge']]).toarray()
        badgesdf = pd.DataFrame(badges, columns=oh.get_feature_names_out())
        train_users = pd.concat([train_users, badgesdf], axis=1)
        
        # save the pipeline transformations to the main model
        self.model = m4.fit(train_users[['past_purchase_amt', 'age', 'badge_bronze', 'badge_gold', 'badge_silver', 'time']], train_y['y'])

        return train_users
    
    def predict(self, test_users, test_logs):
        
        # make column for each badge to add more features
        oh = OneHotEncoder()
        badges = oh.fit_transform(test_users[['badge']]).toarray()
        badgesdf = pd.DataFrame(badges, columns=oh.get_feature_names_out())
        test_users = pd.concat([test_users, badgesdf], axis=1)
        
        # make a dictionary to add new column about time spent on webpage
        time = {}
        for row in test_logs.itertuples():
            try:
                time[row.user_id] += row.seconds
            except:
                time[row.user_id] = row.seconds
                
        # add time column to test_users DataFrame
        time_df = pd.DataFrame.from_dict(time, orient='index')
        test_users = test_users.set_index('user_id').join(time_df).reset_index()
        test_users = test_users.rename(columns={0: "time"})
        test_users = test_users.fillna(0)
        
        # use the fitted model to predict the y values
        return self.model.predict(test_users[['past_purchase_amt', 'age', 'badge_bronze', 'badge_gold', 'badge_silver', 'time']])