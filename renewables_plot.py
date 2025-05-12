import streamlit as st 
import altair as alt
import pandas as pd

def create_renewables_plot(df):

    df_long = df.reset_index().melt(
        id_vars=["datetime", "Source"],
        value_vars=["solar", "wind_onshore", "wind_offshore"],
        var_name="Energy Type",
        value_name="Value"
    )

    # Create label for coloring
    df_long["Type"] = df_long["Source"] + " " + df_long["Energy Type"].str.replace("_", " ").str.title()

    # Define custom color map
    color_map = {
        "Measured Solar": "green",
        "Predicted Solar": "red",
        "Measured Wind Onshore": "lightgreen",
        "Predicted Wind Onshore": "salmon",
        "Measured Wind Offshore": "darkgreen",
        "Predicted Wind Offshore": "darkred",
    }

    chart = alt.Chart(df_long).mark_bar().encode(
        x=alt.X('datetime:T', title='Datetime'),
        y=alt.Y('Value:Q', title='Energy (MW)'),
        color=alt.Color('Type:N', 
                        scale=alt.Scale(domain=list(color_map.keys()), range=list(color_map.values())),
                        legend=alt.Legend(title="Energy Type and Source")  # Custom legend title
        ),
        tooltip=['datetime:T', 'Type:N', 'Value:Q']
    ).properties(
        title="Measured and Predicted Renewable Energy",
        width='container'
    )

    st.altair_chart(chart, use_container_width=True)
