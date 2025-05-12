import streamlit as st


import pickle
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import altair as alt
import pandas as pd
import xgboost as xgb

from datetime import datetime, timedelta
from energy_functions import *

def predict_energy(selected_country_df):
    # Get selected country infromation
    zone = selected_country_df["Zone"][0]
    country_code = selected_country_df["Forecast"][0]

    # Define timespan
    today = datetime.today().strftime('%Y-%m-%d')
    yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    last_week = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')
    next_week = (datetime.today() + timedelta(days=7)).strftime('%Y-%m-%d')

    # Getting price data
    yesterday = '2025-05-08'
    last_week = '2025-05-08'
    print(last_week)
    api_url = f"https://api.energy-charts.info/price?bzn={zone}&start={last_week}&end={yesterday}"
    price = parse_energy_api(api_url)

    # Getting public power
    api_url = f"https://api.energy-charts.info/public_power?country={country_code}&start={last_week}&end={yesterday}"
    public_power = parse_production_api_from_url(api_url)

    # solar should be first in list
    production_types = ['solar','wind_onshore', 'wind_offshore', 'load'] 

    for production_type in production_types:
        api_url = f"https://api.energy-charts.info/public_power_forecast?country=de&production_type={production_type}&forecast_type=day-ahead"
        public_power_forecast = parse_energy_api(api_url)
        print(production_type)
        if production_type == 'solar':
            public_power_forecast = public_power_forecast.rename(columns={"forecast_values": f"{production_type}"})
            forecasts = public_power_forecast.copy()
        else:
            public_power_forecast = public_power_forecast.rename(columns={"forecast_values": f"{production_type}"})
            forecasts = pd.concat([forecasts, public_power_forecast])

    # Considering mean power forecasts every hour
    forecasts = forecasts.resample('h').mean()
    # forecasts = forecasts[forecasts.index.minute == 0]
    forecasts = add_datetime_features(forecasts, datetime_col='datetime')
    forecasts = encode_datetime(forecasts)

    # Considering pubilic power at full hours
    public_power = public_power[public_power.index.minute == 0]
    public_power = add_datetime_features(public_power, datetime_col='datetime')
    public_power = encode_datetime(public_power)

    # Loading model
    file_name = f"./models/xgb_reg_{zone}.pkl"
    model = pickle.load(open(file_name, "rb"))

    FEATURES = ['load', 'solar', 'wind_onshore', 'wind_offshore', 'month_sin',	'month_cos', 'day_sin', 'day_cos', 'hour_sin', 'hour_cos']
    
    # Making predictions for forecast and on last weeks data
    X_pred = forecasts.loc[:,FEATURES]
    y_pred = model.predict(X_pred)

    X_prev = public_power.loc[:,FEATURES]
    y_prev = model.predict(X_prev)

    predictions = pd.DataFrame(data=y_pred, index=X_pred.index, columns=['forecasted_price'])
    combined = price.join(predictions, how='outer')

    predictions = pd.DataFrame(data=y_prev, index=X_prev.index, columns=['last_weeks_forecast'])
    combined = combined.join(predictions, how='outer')

    combined = combined.reset_index()

    return combined

def create_prediction_plot(combined, selected_country_df):
    print(combined.head())
    zone = selected_country_df["Zone"][0]

    label_map = {
        'price': 'Actual Price',
        'forecasted_price': 'Forecasted Price',
        'last_weeks_forecast': "Last Week's Forecast"
    }

    # Melt the DataFrame to long format for Altair
    df_plot = combined.melt(
        id_vars='datetime',
        value_vars=['price', 'forecasted_price', 'last_weeks_forecast'],
        var_name='type',
        value_name=f'{zone} spot price'
    )

    chart = alt.Chart(df_plot).mark_line().encode(
        x=alt.X('datetime:T', title='Datetime'),
        y=alt.Y(f'{zone} spot price:Q', title=f'{zone} Spot Price'),
        
        color=alt.Color(
            'type:N',
            title='Legend',
            scale=alt.Scale(
                domain=list(label_map.keys()),
                range=['green', 'red', 'red']
            ),
            legend=alt.Legend(
                labelExpr=f'datum.label === "price" ? "{label_map["price"]}" : '
                        f'datum.label === "forecasted_price" ? "{label_map["forecasted_price"]}" : '
                        f'"{label_map["last_weeks_forecast"]}"'
            )
        ),
        
        strokeDash=alt.StrokeDash(
            'type:N',
            scale=alt.Scale(
                domain=list(label_map.keys()),
                range=[[], [5, 5], [1, 3]]
            )
        ),
        
        strokeWidth=alt.StrokeWidth(
            'type:N',
            scale=alt.Scale(
                domain=list(label_map.keys()),
                range=[2.5, 1, 1.5]
            )
        )
    ).properties(
        width=1200,
        height=400,
        title="Spot Price Forecast Visualization"
    )

    # Display the chart in Streamlit
    st.altair_chart(chart, use_container_width=True)
    st.text("*Should not be considered financial advice")
