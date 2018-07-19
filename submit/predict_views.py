
# coding: utf-8

# In[108]:


import pandas as pd
import numpy as np
from sklearn.metrics import make_scorer
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import GridSearchCV


# In[109]:


def mape(y, y_pred):
    return np.mean(np.abs((y - y_pred) / y)) * 100
mape_scorer = make_scorer(mape, greater_is_better = False)


# ## Load Data

# In[110]:


train = pd.read_csv("../data/training_set.csv")
train_y = np.ravel(train.groupby(by = ["Game_ID"]).sum().values)
train = train.drop(["Country", "Rounded Viewers", "Game_ID"], axis = 1)
test = pd.read_csv("../data/test_set.csv").drop("Total_Viewers", axis = 1)
ids = test.pop("Game_ID")
game_data = pd.read_csv("../data/game_data.csv")
player_data = pd.read_csv("../data/player_data.csv")


# ## Preprocess

# In[111]:


for column in ["Away_Team", "Home_Team"]:
    train[column] = train[column].astype('category')

t1 = train.drop_duplicates().reset_index().drop("index", axis = 1)
t2 = pd.get_dummies(t1, columns = ["Away_Team", "Home_Team"])
season_encoder = LabelEncoder()
date_encoder = LabelEncoder()
t2["Season"] = season_encoder.fit_transform(t2["Season"])
t2["Game_Date"] = date_encoder.fit_transform(t2["Game_Date"])
test["Season"] = season_encoder.transform(test["Season"])
test["Game_Date"] = date_encoder.transform(test["Game_Date"])
test = pd.get_dummies(test, columns = ["Away_Team", "Home_Team"])


# ## Model

# In[112]:


get_ipython().run_cell_magic('time', '', "model = RandomForestRegressor(n_jobs = 4)\n\nparams = {'max_depth'        : [None],\n          'criterion'        : ['mae'],\n          'min_samples_leaf' : [30],\n          'min_samples_split': [100],\n          'n_estimators'     : [40, 50, 60, 70, 80, 90]}\ngrid_search = GridSearchCV(estimator = model, cv = 5, verbose = 1, \n                           param_grid = params, scoring = mape_scorer, \n                           return_train_score = True, refit = True)\ngrid_search.fit(X = t2, y = train_y)")


# In[113]:


grid_search.best_params_


# In[117]:


predictions = pd.Series(grid_search.predict(test))
testOut = pd.read_csv("../data/test_set.csv")
testOut["Total_Viewers"] = predictions.values
testOut.to_csv("../submit/test_set_Organic_Bike.csv")

