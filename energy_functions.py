import requests
import numpy as np
import pandas as pd

from sklearn.preprocessing import FunctionTransformer

def parse_energy_api(api_url):
    """
    Fetches JSON from an Energy-Charts API endpoint and returns a DataFrame
    with the timestamp converted from unix_seconds. Assumes all other fields
    are same-length lists.
    """
    response = requests.get(api_url)
    data = response.json()

    if 'unix_seconds' not in data:
        raise ValueError("Missing 'unix_seconds' in API response")

    # timestap field 
    df_dict = {
        'datetime': pd.to_datetime(data['unix_seconds'], unit='s')
    }

    for key, value in data.items():
        if key != 'unix_seconds' and isinstance(value, list) and len(value) == len(data['unix_seconds']):
            df_dict[key] = value
    df = pd.DataFrame(df_dict)
    df = df.set_index('datetime')
    return df


def parse_production_api_from_url(api_url):
    """
    Fetches and parses energy production data from a given API URL.
    Handles 'unix_seconds' as timestamp and flattens named production series.
    Returns a cleaned pandas DataFrame.
    """
    response = requests.get(api_url)
    response.raise_for_status()
    data = response.json()

    # Validate expected keys
    unix_seconds = data.get("unix_seconds")
    prod_types = data.get("production_types")
    if not unix_seconds or not isinstance(unix_seconds, list):
        raise ValueError("Missing or invalid 'unix_seconds'")
    if not prod_types or not isinstance(prod_types, list):
        raise ValueError("Missing or invalid 'production_types'")

    # Create DataFrame with timestamps
    df = pd.DataFrame({
        "datetime": pd.to_datetime(unix_seconds, unit="s")
    })

    for prod in prod_types:
        name = prod.get("name")
        values = prod.get("data")
        if name and isinstance(values, list) and len(values) == len(unix_seconds):
            col_name = name.strip().lower().replace(" ", "_")
            df[col_name] = values
    df = df.set_index('datetime')
    return df


def add_datetime_features(df, datetime_col='datetime'):

    df['month'] = df.index.month
    df['day_of_week'] = df.index.dayofweek + 1  # 1 = Monday, 7 = Sunday
    df['hour'] = df.index.hour  # 1–24
    return df

def sin_transformer(column, period):
    return FunctionTransformer(lambda df: np.sin(df[[column]] / period * 2 * np.pi))

def cos_transformer(column, period):
    return FunctionTransformer(lambda df: np.cos(df[[column]] / period * 2 * np.pi))

def encode_datetime(feature_df):
    feature_df["month_sin"] = sin_transformer("month", 12).fit_transform(feature_df)
    feature_df["month_cos"] = cos_transformer("month", 12).fit_transform(feature_df)
    
    feature_df["day_sin"] = sin_transformer("day_of_week", 7).fit_transform(feature_df)
    feature_df["day_cos"] = cos_transformer("day_of_week", 7).fit_transform(feature_df)
    
    feature_df["hour_sin"] = sin_transformer("hour", 24).fit_transform(feature_df)
    feature_df["hour_cos"] = cos_transformer("hour", 24).fit_transform(feature_df)

    return feature_df