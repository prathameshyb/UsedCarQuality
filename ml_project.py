# -*- coding: utf-8 -*-
"""ml_project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15bLniXSvIFil3Cq4skM6E2jX6-c6-bdv

# Course Project - Real-World Machine Learning Model

##Used Car Quality Detection
One of the biggest challenges of an auto dealership purchasing a used car at an auto auction is the risk of that the vehicle might have serious issues that prevent it from being sold to customers. The auto community calls these unfortunate purchases "kicks".The challenge of this project is to predict if the car purchased at the Auction is a Kick (bad buy).
"""

!pip install jovian --upgrade -q

"""##Downloading the Dataset
Here we'll be downloading our required dataset from kaggle by using opendataset.
"""

!pip install jovian opendatasets --upgrade --quiet

dataset_url='https://www.kaggle.com/competitions/DontGetKicked/data'



import opendatasets as od
od.download(dataset_url)

data_dir='/content/DontGetKicked'

"""The dataset has been downloaded and extracted."""

import os
os.listdir(data_dir)

"""## Data Preparation and Cleaning

Here we'll be dealing with empty,null and missing as well as wromg values by replacing them with either 0 or average values

"""

!pip install numpy pandas-profiling matplotlib seaborn --quiet
!pip install jovian opendatasets xgboost graphviz lightgbm scikit-learn xgboost lightgbm --upgrade --quiet

# Commented out IPython magic to ensure Python compatibility.
import opendatasets as od
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib
import jovian
import os
# %matplotlib inline

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 150)
sns.set_style('darkgrid')
matplotlib.rcParams['font.size'] = 14
matplotlib.rcParams['figure.figsize'] = (10, 6)
matplotlib.rcParams['figure.facecolor'] = '#00000000'

import pandas as pd

raw_df=pd.read_csv('/content/DontGetKicked/training.csv')

raw_df

"""## Preparing the Data for Training

We'll perform the following steps to prepare the dataset for training:

1. Create a train/test/validation split
2. Identify input and target columns
3. Identify numeric and categorical columns
4. Impute (fill) missing numeric values
5. Scale numeric values to the $(0, 1)$ range
6. Encode categorical columns to one-hot vectors
"""

from sklearn.model_selection import train_test_split

test_df=pd.read_csv('/content/DontGetKicked/test.csv')

"""So we'll be splitting the data into 75:25 ratio for training and validation"""

train_df, val_df = train_test_split(raw_df, test_size=0.25, random_state=42)

train_df

"""testing data has been provided in the dataset
As we don't have results for test inputs, we cant check accuracy for test dataset from kaggle.
"""

test_df

"""taking input and result columns saparetly"""

input_cols=list(train_df.columns)[2:]
target_cols='IsBadBuy'

train_inputs=train_df[input_cols]
train_targets=train_df[target_cols]

val_inputs=val_df[input_cols]
val_targets=val_df[target_cols]

train_targets

"""Dividing columns into numeric and categorical types"""

numeric_cols = train_inputs.select_dtypes(include=np.number).columns.tolist()
categorical_cols = train_inputs.select_dtypes('object').columns.tolist()

print(categorical_cols)

"""Machine learning models can't work with missing numerical data. The process of filling missing values is called imputation . which is done by replacing missing values with the average value in the column using the SimpleImputer class from sklearn.impute."""

from sklearn.impute import SimpleImputer

imputer = SimpleImputer(strategy = 'mean').fit(raw_df[numeric_cols])

train_inputs[numeric_cols] = imputer.transform(train_inputs[numeric_cols])
val_inputs[numeric_cols] = imputer.transform(val_inputs[numeric_cols])

"""Scaling numeric features ensures that no particular feature has a disproportionate impact on the model's loss."""

from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler().fit(raw_df[numeric_cols])

val_inputs[numeric_cols].isna().sum()

train_inputs[numeric_cols] = scaler.transform(train_inputs[numeric_cols])
val_inputs[numeric_cols] = scaler.transform(val_inputs[numeric_cols])

val_inputs.describe().loc[['min', 'max']]

train_inputs[numeric_cols]

"""One hot encoding involves adding a new binary (0/1) column for each unique category of a categorical column."""

from sklearn.preprocessing import OneHotEncoder
encoder = OneHotEncoder(sparse=False, handle_unknown='ignore').fit(raw_df[categorical_cols])

encoded_cols = list(encoder.get_feature_names_out(categorical_cols))

train_inputs[encoded_cols] = encoder.transform(train_inputs[categorical_cols])
val_inputs[encoded_cols] = encoder.transform(val_inputs[categorical_cols])
#test_inputs[encoded_cols] = encoder.transform(test_inputs[categorical_cols])

X_train = train_inputs[numeric_cols + encoded_cols]
X_val = val_inputs[numeric_cols + encoded_cols]

"""##Desicion Tree
A decision tree in general parlance represents a hierarchical series of binary decisions.
We can use DecisionTreeClassifier from sklearn.tree to train a decision tree.
"""

from sklearn.tree import DecisionTreeClassifier
model = DecisionTreeClassifier(random_state=42)

X_train

# Commented out IPython magic to ensure Python compatibility.
# %%time
# model.fit(X_train, train_targets)

"""Accuracy score"""

from sklearn.metrics import accuracy_score, confusion_matrix

train_preds = model.predict(X_train)
train_preds

pd.value_counts(train_preds)

accuracy_score(train_targets, train_preds)

"""Overfitting of data by the model from training data"""

model.score(X_val, val_targets)

"""We can visualize the decision tree learned from the training data."""

from sklearn.tree import plot_tree, export_text
plt.figure(figsize=(80,20))
plot_tree(model, feature_names=X_train.columns, max_depth=2, filled=True);

tree_text = export_text(model, max_depth=10, feature_names=list(X_train.columns))
print(tree_text[:5000])

"""Importance of features in decision tree"""

importance_df = pd.DataFrame({
    'feature': X_train.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)
importance_df.head(10)

plt.title('Feature Importance')
sns.barplot(data=importance_df.head(10), x='importance', y='feature');

"""##Hyperparameter Tuning and Overfitting
The DecisionTreeClassifier accepts several arguments, some of which can be modified to reduce overfitting.The DecisionTreeClassifier accepts several arguments, some of which can be modified to reduce overfitting.
"""

model = DecisionTreeClassifier(max_depth=4, random_state=42)

model.fit(X_val, val_targets)
model.score(X_train, train_targets)
model.score(X_val, val_targets)

print(export_text(model, feature_names=list(X_train.columns)))

def max_depth_error(md):
    model = DecisionTreeClassifier(max_depth=md, random_state=42)
    model.fit(X_train, train_targets)
    train_acc = 1 - model.score(X_train, train_targets)
    val_acc = 1 - model.score(X_val, val_targets)
    return {'Max Depth': md, 'Training Error': train_acc, 'Validation Error': val_acc}

# Commented out IPython magic to ensure Python compatibility.
# %%time
# errors_df = pd.DataFrame([max_depth_error(md) for md in range(1, 21)])
# plt.figure()
# plt.plot(errors_df['Max Depth'], errors_df['Training Error'])
# plt.plot(errors_df['Max Depth'], errors_df['Validation Error'])
# plt.title('Training vs. Validation Error')
# plt.xticks(range(0,21, 2))
# plt.xlabel('Max. Depth')
# plt.ylabel('Prediction Error (1 - Accuracy)')
# plt.legend(['Training', 'Validation'])

model = DecisionTreeClassifier(max_depth=6, random_state=42).fit(X_train, train_targets)
model.score(X_val, val_targets)

def max_leaf_nodes_error(md):
    model = DecisionTreeClassifier(max_leaf_nodes=md, random_state=42)
    model.fit(X_train, train_targets)
    train_acc = 1 - model.score(X_train, train_targets)
    val_acc = 1 - model.score(X_val, val_targets)
    return {'Max_Leaf_Nodes': md, 'Training Error': train_acc, 'Validation Error': val_acc}

# Commented out IPython magic to ensure Python compatibility.
# %%time
# errors_df = pd.DataFrame([max_leaf_nodes_error(md) for md in range(2, 21)])
# plt.figure()
# plt.plot(errors_df['Max_Leaf_Nodes'], errors_df['Training Error'])
# plt.plot(errors_df['Max_Leaf_Nodes'], errors_df['Validation Error'])
# plt.title('Training vs. Validation Error')
# plt.xticks(range(0,21, 2))
# plt.xlabel('Max. Leaf Nodes')
# plt.ylabel('Prediction Error (1 - Accuracy)')
# plt.legend(['Training', 'Validation'])

"""##Random Forest
While tuning the hyperparameters of a single decision tree may lead to some improvements, a much more effective strategy is to combine the results of several decision trees trained with slightly different parameters. This is called a random forest model.
We'll use the RandomForestClassifier class from sklearn.ensemble.
"""

from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier(n_jobs=-1, random_state=42)

# Commented out IPython magic to ensure Python compatibility.
# %%time
# model.fit(X_train, train_targets)
# model.score(X_train, train_targets)

"""Overfitting of data"""

model.score(X_val, val_targets)

train_probs = model.predict_proba(X_train)
train_probs

importance_df = pd.DataFrame({
    'feature': X_train.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)
importance_df.head(10)

import math

(math.factorial(88))%89

plt.title('Feature Importance')
sns.barplot(data=importance_df.head(10), x='importance', y='feature');

"""##Hyperparameter Tuning
Just like decision trees, random forests also have several hyperparameters. In fact many of these hyperparameters are applied to the underlying decision trees.
"""

base_model = RandomForestClassifier(random_state=42, n_jobs=-1).fit(X_train, train_targets)

base_train_acc = base_model.score(X_train, train_targets)
base_val_acc = base_model.score(X_val, val_targets)
base_accs = base_train_acc, base_val_acc
base_accs

model = RandomForestClassifier(random_state=42, n_jobs=-1, n_estimators=10)
model.fit(X_train, train_targets)
model.score(X_train, train_targets), model.score(X_val, val_targets)

model = RandomForestClassifier(random_state=42, n_jobs=-1, n_estimators=500)
model.fit(X_train, train_targets)

model.score(X_train, train_targets)
model.score(X_val, val_targets)

def test_params(**params):
    model = RandomForestClassifier(random_state=42, n_jobs=-1, **params).fit(X_train, train_targets)
    return model.score(X_train, train_targets), model.score(X_val, val_targets)

def test_param_and_plot(param_name, param_values):
    train_scores, val_scores = [], []
    for value in param_values:
        params = {param_name: value}
        train_score, val_score = test_params(**params)
        train_scores.append(train_score)
        val_scores.append(val_score)
    plt.figure(figsize=(10,6))
    plt.title('Overfitting curve: ' + param_name)
    plt.plot(param_values, train_scores, 'b-o')
    plt.plot(param_values, val_scores, 'r-o')
    plt.xlabel(param_name)
    plt.ylabel('Score')
    plt.legend(['Training', 'Validation'])

test_param_and_plot('max_depth', [5, 10, 15, 20, 25, 30, 35])

test_param_and_plot('n_estimators', [5, 10, 15, 20, 25, 30, 35])

test_param_and_plot('max_features',['sqrt','log2',10])

test_param_and_plot('min_weight_fraction_leaf',[0,0.1,0.2,0.3,0.4,0.5])

"""Let's train a random forest with customized hyperparameters based on our learnings. Of course, different hyperpraams"""

model = RandomForestClassifier(n_jobs=-1,
                               random_state=42,
                               n_estimators=20,
                               max_features='sqrt',
                               max_depth=35)
model.fit(X_train, train_targets)
model.score(X_train, train_targets), model.score(X_val, val_targets)

X_val.info()

"""##Making Predictions on New Inputs

As we don't have results for test inputs, we cant check accuracy for test dataset from kaggle.
"""

def predict_input(model, single_input):
    input_df = pd.DataFrame([single_input])
    input_df[numeric_cols] = imputer.transform(input_df[numeric_cols])
    input_df[numeric_cols] = scaler.transform(input_df[numeric_cols])
    input_df[encoded_cols] = encoder.transform(input_df[categorical_cols])
    X_input = input_df[numeric_cols + encoded_cols]
    pred = model.predict(X_input)[0]
    prob = model.predict_proba(X_input)[0][list(model.classes_).index(pred)]
    return pred, prob

"""Entering manual values  """

ip={'PurchDate':'12/14/2009','VehYear':0.222222,'WheelTypeID':1,'VehOdo':0.587806,'MMRAcquisitionAuctionAveragePrice': 0.156822,'MMRAcquisitonRetailCleanPrice':0.106432,'MMRCurrentAuctionAveragePrice':0.071497,'MMRCurrentAuctionCleanPrice':0.095065,'MMRCurrentRetailAveragePrice':0.083367,
    'BYRNO':0.047621,'VNZIP1':0.800819,'VehBCost':0.149534,'IsOnlineSale':0.0,'WarrantyCost':0.203383,'PurchDate_1/10/2010':1.0,'Auction_OTHER':1.0,'Make_ACURA':1.0,'Model_1500 RAM PICKUP 4WD	':1.0,'Trim_250':1.0,'SubModel_2D CONVERTIBLE GL	':1.0,'Color_BLACK':1.0	,'Transmission_Manual':1.0,
    'Nationality_AMERICAN':1.0,'Size_LARGE ':1.0,'TopThreeAmericanName_FORD':1.0,'VNST_UT':1.0,'VehicleAge':0.236554,'MMRAcquisitionAuctionCleanPrice':0.266631,'MMRCurrentRetailCleanPrice':0.616321,'MMRAcquisitionRetailAveragePrice':0.484613
    ,'Auction':'ADESA', 'Make':'DODGE', 'Model':'NEON', 'Trim':'', 'SubModel':'4D SUV', 'Color':'RED', 'Transmission':'AUTOMATIC', 'WheelType':'nan', 'Nationality':'AMERICAN', 'Size':'LARGE', 'TopThreeAmericanName':'GM', 'PRIMEUNIT':'YES', 'AUCGUART':'GREEN', 'VNST':'GA'}

predict_input(model, ip)

"""#### Inferences and Conclusion

In this case study we have analysed the data to predict if a car purchase is worth of price or bad one using dataset from kaggle.
The conclusions are:

**From Decision tree model**
*   Wheel type is the most importnt feature deciding the price of car
*   Max depth of 6 levels is most useful to get maximum score in validation data

 **From Random Forest Model**

*  n estimatorrs after 10 doest not contribute much in accuracy score
*   0.1 is most close to ideal minimum weight fraction of leaf.

##References and Future Work
The dataset has following future scope :



*   Instead of fatewise classifying, by month or by period classification would be helpful for lightweight dataset.

*   Detailed analysis about actual purchased cost and appropriate cost can be done
*   Less important features such as colour can be emitted to imporove computing speed


*   Another parameter insurance claim or past accident history can be added
"""

pip install jovian --upgrade

import jovian

jovian.commit()