import streamlit as st

from country_selection import select_country, create_country_selection_plot
from energy_prediction import predict_energy, create_prediction_plot
from renewables_plot import create_renewables_plot


with st.sidebar:
    st.title("About")
    st.text("- Select a country from the drop down menu. \n" \
    "- Available countries are colored in light green. \n" \
    "- The current selection is colored in dark green \n")
    st.write("Created in :streamlit: by Tara Sassel")

st.title("Energy Spot Price Prediction")

selected_country_df, europe = select_country()
create_country_selection_plot(europe)

combined_predictions, renewables = predict_energy(selected_country_df)
create_prediction_plot(combined_predictions, selected_country_df)

create_renewables_plot(renewables)
st.text("*This project should not be considered financial advice.")