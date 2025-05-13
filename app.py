import streamlit as st

from country_selection import select_country, create_country_selection_plot
from energy_prediction import predict_energy, create_prediction_plot
from renewables_plot import create_renewables_plot


with st.sidebar:
    st.title("About")
    st.text("This Streamlit app visualizes the predicted energy spot price of diffrent countries." \
    "Load, renewable energy generation such as solar and wind (offshore and onshore) are used to make those predictions." \
    "Diffrent models are used for the predictions depending on the selected country." \
    "Feature engineering was performed to optimize the models performance." \
    "The data is obtained via API requests from Energy-Charts.info, using data licensed under CC BY 4.0.")
    
    st.write("Created in :streamlit: by Tara Sassel")

st.title("Energy Spot Price Prediction")

selected_country_df, europe = select_country()
create_country_selection_plot(europe)

combined_predictions, renewables = predict_energy(selected_country_df)
create_prediction_plot(combined_predictions, selected_country_df)

create_renewables_plot(renewables)
st.text("*This project should not be considered financial advice.")