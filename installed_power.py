import streamlit as st
import requests
import pandas as pd 


def get_installed_power(selected_country_df):

    country_code = selected_country_df["Forecast"][0]
    url = f"https://api.energy-charts.info/installed_power?country={country_code}&time_step=yearly&installation_decommission=false"
    response = requests.get(url)
    data = response.json()

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