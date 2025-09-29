import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
import numpy as np

def heart_disease_features(df):
    # Numeric features, no missing values assumed
    return df

def telco_churn_features(df):
    # Example: encode categorical, scale numeric
    df = df.copy()
    # Encode categorical columns
    for col in df.select_dtypes(include=['object']).columns:
        if col != 'target' and col != 'Churn':
            df[col] = LabelEncoder().fit_transform(df[col].astype(str))
    # Fill missing values
    df = df.fillna(df.median(numeric_only=True))
    # Scale numeric columns
    scaler = StandardScaler()
    num_cols = df.select_dtypes(include=[np.number]).columns
    df[num_cols] = scaler.fit_transform(df[num_cols])
    return df

def get_features(df, dataset):
    if dataset == 'heart':
        return heart_disease_features(df)
    elif dataset == 'telco':
        return telco_churn_features(df)
    else:
        raise ValueError('Unknown dataset type')
