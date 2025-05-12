import streamlit as st

from country_selection import select_country, create_country_selection_plot
from energy_prediction import predict_energy, create_prediction_plot
from renewables_plot import create_renewables_plot


st.title("Energy Spot Price Prediction")

selected_country_df, europe = select_country()
create_country_selection_plot(europe)

combined_predictions, renewables = predict_energy(selected_country_df)
create_prediction_plot(combined_predictions, selected_country_df)

create_renewables_plot(renewables)
st.text("*This project should not be considered financial advice.")